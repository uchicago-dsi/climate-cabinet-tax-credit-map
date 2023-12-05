/**
 * API route for geography boundary requests.
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
 * Fetches a report for a given geometry based on id. The
 * report consists of the geometry boundary and boundaries
 * for the tax credit bonus territories it intersects,
 * among other metadata.
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
                geotype.name AS geography_type,
                CASE
                    WHEN geo.id = ${geographyId} THEN TRUE
                    ELSE FALSE
                END AS is_target,
                CASE
                    WHEN geo.id = ${geographyId} THEN ST_ENVELOPE(geo.boundary)
                    ELSE null
                END AS bbox
            FROM tax_credit_geography AS geo
            JOIN tax_credit_geography_type AS geotype
                ON geotype.id = geo.geography_type_id
            WHERE geo.id IN (${geographyId}) OR geo.id IN (
                SELECT bonus_geography_id
                FROM tax_credit_target_bonus_assoc
                WHERE target_geography_id = ${geographyId}
            )
            GROUP BY(geo.id, geotype.name)
        ) AS t
    `;
  let geographies = rawGeos.map((r) => JSON.parse(r.data));

  // Query DB for tax credit programs related to geographies
  let geoIds = geographies.map((g) => g.properties.id);
  let programs = await prisma.$queryRaw`
        SELECT DISTINCT
            geo_type.name AS geography_type,
            program.name AS program_name,
            program.agency AS program_agency,
            program.description AS program_description,
            program.base_benefit AS program_base_benefit,
            geo_type_program.amount_description AS program_amount_description
        FROM tax_credit_geography AS geo
        JOIN tax_credit_geography_type AS geo_type
            ON geo_type.id = geo.geography_type_id
        JOIN tax_credit_geography_type_program AS geo_type_program
            ON geo_type_program.geography_type_id = geo_type.id
        JOIN tax_credit_program AS program
            ON program.id = geo_type_program.program_id
        WHERE geo.id IN (${Prisma.join(geoIds)});`;

  let summaryStats = await prisma.$queryRaw`
        WITH block_groups AS (
            SELECT DISTINCT ON (bg.id, geotype.name)
                bg.id AS block_group_id,
                population,
                geo.id AS geo_id,
                geo.name,
                geotype.name AS type
            FROM tax_credit_census_block_group AS bg
            JOIN tax_credit_geography AS geo
                ON ST_Within(bg.centroid, geo.boundary)
            JOIN tax_credit_geography_type AS geotype
                ON geotype.id = geo.geography_type_id
            WHERE (
                geo.id IN (${geographyId})
                OR geo.id IN (
                    SELECT bonus_geography_id
                    FROM tax_credit_target_bonus_assoc
                    WHERE target_geography_id = ${geographyId}
                )
            )
            ORDER BY bg.id, geotype.name
        ),
        target_block_groups AS (
            SELECT *
            FROM block_groups
            WHERE geo_id = ${geographyId}
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
  const bigIntHandler = (key, value) =>
    typeof value === "bigint"
      ? value.toString() // convert BigInt to string
      : value; // return everything else unchanged

  // Compose final response payload
  let payload = {
    geographies: geographies,
    programs: programs,
    summaryStats: JSON.stringify(summaryStats, bigIntHandler),
  };

  console.log("payload", payload);

  return NextResponse.json(payload, bigIntHandler);
}
