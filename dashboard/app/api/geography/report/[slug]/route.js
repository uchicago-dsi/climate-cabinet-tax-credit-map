/**
 * API route for geography boundary requests.
 * 
 * References:
 * - https://nextjs.org/docs/app/api-reference/functions/next-request
 * - https://nextjs.org/docs/app/api-reference/functions/next-response
 */

"server only"

import prisma from "@/lib/db";
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
    let { slug } = params;
    let geographyId = parseInt(slug);
    let rows = await prisma.$queryRaw`
        SELECT ST_ASGeoJSON(t.*) AS data
        FROM (
            SELECT
                candidates.id,
                candidates.name,
                candidates.as_of,
                candidates.source,
                geo_type.name AS geography_type,
                candidates.boundary AS boundary,
                CASE
                    WHEN candidates.id = ${geographyId} THEN 1 
                    ELSE 0
                END AS is_target
            FROM tax_credit_geography AS candidates
            CROSS JOIN (
                SELECT
                    boundary,
                    ST_Envelope(boundary) as bbox
                FROM tax_credit_geography
                WHERE id = ${geographyId}
            ) target
            JOIN tax_credit_geography_type AS geo_type ON
                geo_type.id = candidates.geography_type_id
            WHERE candidates.boundary && target.bbox AND 
                ST_Intersects(candidates.boundary, target.boundary)
            ) AS t
        WHERE geography_type != 'state';
    `;
    let geographies = rows.map(r => JSON.parse(r.data));
    return NextResponse.json(geographies);
}
