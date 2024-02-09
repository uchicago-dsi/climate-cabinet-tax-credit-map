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
  let formattedSearchTerm = searchTerm.replace(/\s+/g, ' & ');
  let data = await prisma.$queryRaw`
    SELECT * FROM
      (
        SELECT 
          id::varchar(255), 
          name,
          geography_type,
          ts_rank(
            name_vector, 
            to_tsquery('english', ${formattedSearchTerm})
          ) as rank,
          similarity(${searchTerm}, name) as sml
        FROM tax_credit_geography
        WHERE geography_type IN (
          'county',
          'municipal utility',
          'municipality',
          'rural cooperative',
          'state'
        )
        ORDER BY rank DESC, sml DESC, name ASC
        LIMIT ${limit}
      ) as results
      WHERE rank > 1e-20 OR sml > 0
    `;
  return NextResponse.json({ data });
}
