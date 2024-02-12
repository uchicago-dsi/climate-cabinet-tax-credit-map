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
 * top results as a list of objects with "id", "name",
 * and "geography_type" properties. Full-text search
 * is achieved in PostgreSQL using a combination of 
 * similarity scores calculated from trigrams ("pg_trgm")
 * and ranks calculated from normalized vectors of 
 * lexemes ("tsvector").
 *
 *  @param {NextRequest} - The HTTP request. Contains the
 *      search term and the number of matches to return.
 */
export async function POST(request) {
  let { searchPhrase, limit } = await request.json();
  let formattedSearchPhrase = searchPhrase.replace(/\s+/g, ' ').trim();
  let tsquerySearchPhrase = formattedSearchPhrase.replace(/\s+/g, ' & ');

  let data = await prisma.$queryRaw`
    SELECT
      id,
      name, 
      geography_type
    FROM
      (
        SELECT 
          id::varchar(255), 
          name,
          geography_type,
          CASE
            WHEN geography_type = 'state' THEN 1
            ELSE 0
          END AS geography_rank,
          ts_rank(
            name_vector, 
            to_tsquery('english', ${tsquerySearchPhrase})
          ) AS rank,
          similarity(${formattedSearchPhrase}, name) AS sml
        FROM tax_credit_geography
        WHERE geography_type IN (
          'county',
          'municipal utility',
          'municipality',
          'rural cooperative',
          'state'
        )
        ORDER BY sml DESC, rank DESC, geography_rank DESC, name ASC
        LIMIT ${limit}
      ) AS results
      WHERE rank > 1e-20 OR sml > 0;
    `;
  return NextResponse.json({ data });
}
