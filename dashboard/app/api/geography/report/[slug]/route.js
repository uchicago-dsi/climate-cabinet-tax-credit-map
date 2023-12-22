/**
 * API route for geography report requests.
 *
 * References:
 * - https://nextjs.org/docs/app/api-reference/functions/next-request
 * - https://nextjs.org/docs/app/api-reference/functions/next-response
 */

"server only";

import prisma from "@/lib/db";
import { Prisma } from "@prisma/client";
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
                CASE
                    WHEN geo.id = ${geographyId} THEN TRUE
                    ELSE FALSE
                END AS is_target,
                CASE
                    WHEN geo.id = ${geographyId} THEN ST_ENVELOPE(geo.geometry)
                    ELSE null
                END AS bbox
            FROM tax_credit_geography AS geo
            WHERE geo.id IN (${geographyId}) OR geo.id IN (
                SELECT bonus_geography_id
                FROM tax_credit_target_bonus_assoc
                WHERE target_geography_id = ${geographyId}
            )
        ) AS t
    `;
  let geographies = rawGeos.map((r) => JSON.parse(r.data));

  // Aggregate population counts in entire target 
  // geography and any overlapping bonus areas
  let geoIds = geographies.map((g) => g.properties.id);
  let summaryStats = await prisma.$queryRaw`
        WITH block_groups AS (
            SELECT DISTINCT ON (bg.id, geo.geography_type)
                bg.id AS block_group_id,
                bg.year,
                population,
                geo.id AS geo_id,
                geo.name,
                geo.geography_type AS type
            FROM tax_credit_census_block_group AS bg
            JOIN tax_credit_geography AS geo
                ON ST_Within(bg.centroid, geo.geometry)
            WHERE geo.id IN (${Prisma.join(geoIds)}) AND year = 2020
        ),
        target_block_groups AS (
            SELECT block_group_id
            FROM block_groups
            WHERE geo_id = ${geographyId} AND year = 2020
        )
        SELECT
            bg.type,
            SUM(bg.population) AS population
        FROM block_groups AS bg
        JOIN target_block_groups AS tbg
            ON bg.block_group_id = tbg.block_group_id
        GROUP BY bg.type;
      `;

  // Handle BigInt values
  const bigIntHandler = (_, value) =>
    typeof value === "bigint"
      ? value.toString()
      : value;

  // Compose final response payload
  let payload = {
    geographies: geographies,
    summaryStats: JSON.stringify(summaryStats, bigIntHandler),
  };

  return NextResponse.json(payload, bigIntHandler);
}
