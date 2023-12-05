/**
 * API route for geography search requests.
 *
 * References:
 * - https://nextjs.org/docs/app/api-reference/functions/next-request
 * - https://nextjs.org/docs/app/api-reference/functions/next-response
 */

"server only";

import prisma from "@/lib/db";
import { NextRequest, NextResponse } from "next/server";

/**
 * Searches for a geography by name and returns the
 * top results as a list of objects with "id" and
 * "name" properties. NOTE: To handle search terms
 * with spaces in Postgres, words must be joined with
 * operators like "boolean and" (&) or "proximity" (<->),
 * which preserves word order.
 *
 *  @param {NextRequest} - The HTTP request. Contains the
 *      search term and the number of matches to return.
 */
export async function POST(request) {
  let { searchTerm, limit } = await request.json();
  let regex = `%${searchTerm.trim().split(" ").join("%")}%`;
  let data = await prisma.$queryRaw`
      SELECT geo.id::varchar(255), geo.name, similarity(geo.name, ${searchTerm}) AS sml
      FROM tax_credit_geography AS geo
      WHERE geo.geography_type_id IN (0, 1, 2, 4) 
        AND geo.name ILIKE ${regex}
      ORDER BY sml DESC
      LIMIT ${limit};
    `;
  return NextResponse.json({ data });
}
