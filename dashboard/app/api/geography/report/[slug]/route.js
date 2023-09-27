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
                geo.as_of,
                geo.source,
                SUM(population) AS total_population,
                CASE
                    WHEN geo.id = ${geographyId} THEN TRUE
                    ELSE FALSE
                END AS is_target,
                geo.simple_boundary AS boundary
            FROM tax_credit_geography AS geo
            JOIN tax_credit_geography_type AS geotype
                ON geotype.id = geo.geography_type_id
            LEFT JOIN tax_credit_census_tract AS census_tract
                ON ST_Within(
                    census_tract.centroid,
                    geo.boundary
                )
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

  // Compose final response payload
  let payload = {
    geographies: geographies,
    programs: programs,
  };

  return NextResponse.json(payload);
}
