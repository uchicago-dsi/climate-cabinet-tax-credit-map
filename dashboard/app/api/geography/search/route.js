/**
 * API route for geography search requests.
 * 
 * References:
 * - https://nextjs.org/docs/app/api-reference/functions/next-request
 * - https://nextjs.org/docs/app/api-reference/functions/next-response
 */

"server only"

import prisma from "@/lib/db";
import { NextRequest, NextResponse } from 'next/server';


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
    let regex = `${searchTerm.trim().split(" ").join("%")}%`;
    let data = await prisma.$queryRaw`
      SELECT id::varchar(255), name
      FROM tax_credit_geography
      WHERE name ILIKE ${regex}
      LIMIT ${limit};
    `;
    return NextResponse.json({ data })
}
