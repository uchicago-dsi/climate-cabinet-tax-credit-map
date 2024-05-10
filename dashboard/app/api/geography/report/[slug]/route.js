/**
 * API route for geography report requests.
 *
 * References:
 * - https://nextjs.org/docs/app/api-reference/functions/next-request
 * - https://nextjs.org/docs/app/api-reference/functions/next-response
 */

"server only";

import prisma from "@/lib/db";
import { NextRequest, NextResponse } from "next/server";

/**
 * Fetches a report for a given geography based on id. The
 * report consists of the geography's name, type,
 * bounding box, total population, and eligible tax credit
 * programs, along with the names, types, and populations of
 * the tax credit bonus territories that the geography intersects.
 *
 *  @param {NextRequest} - The HTTP request. Contains a geography id.
 */
export async function GET(request, { params }) {
  // Query DB for overlapping geographies with metadata
  let { slug } = params;
  let geographyId = parseInt(slug);
  let rawGeos = await prisma.$queryRaw`
        SELECT ST_ASGeoJSON(t.*) AS data
        FROM (
            SELECT
                geo.id,
                geo.name,
                geo.geography_type,
                geo.population,
                CASE
                    WHEN geo.id = ${geographyId}
                      THEN TRUE
                    ELSE FALSE
                END AS is_target,
                CASE
                    WHEN geo.id = ${geographyId}
                      THEN ST_ForcePolygonCCW(geo.geometry)
                    ELSE null
                END AS geometry
            FROM tax_credit_geography AS geo
            WHERE geo.id IN (${geographyId}) OR geo.id IN (
                SELECT bonus_id
                FROM tax_credit_target_bonus_overlap
                WHERE target_id = ${geographyId}
            )
            ORDER BY geo.geography_type
        ) AS t
    `;

  // Parse geographies
  let target = null;
  let bonuses = [];
  for (let i = 0; i < rawGeos.length; i++) {
    let parsed = JSON.parse(rawGeos[i]["data"]);
    let is_target = parsed["properties"]["is_target"];
    delete parsed["properties"]["is_target"];
    if (is_target) {
      target = parsed;
    } else {
      bonuses.push(parsed["properties"]);
    }
  }

  // Return 404 if no target geography was found
  if (target == null) {
    return new NextResponse(`Geography ${geographyId} not found.`, {
      status: 404,
    });
  }

  // Fetch population counts within target-bonus geography overlaps
  let summaryStats = await prisma.$queryRaw`
        SELECT
            geo.geography_type AS geography_type,
            SUM(overlap.population)::INTEGER AS population,
            COUNT(*)::INTEGER AS count,
            geo.programs
        FROM tax_credit_geography AS geo
        JOIN tax_credit_target_bonus_overlap AS overlap
            ON geo.id = overlap.bonus_id
        WHERE overlap.target_id = ${geographyId}
        GROUP BY geo.geography_type, geo.programs;
      `;

  // Parse stats
  let bonusStats = [];
  let programs = new Set();
  for (let i = 0; i < summaryStats.length; i++) {
    let stat = summaryStats[i];
    let statPrograms = stat["programs"];
    statPrograms.forEach((prog) => programs.add(prog));
    delete stat["programs"];
    bonusStats.push(stat);
  }

  // Compose final response payload
  let payload = {
    target: target,
    bonuses: bonuses,
    stats: bonusStats,
    programs: Array.from(programs).sort(),
  };

  return NextResponse.json(payload);
}
