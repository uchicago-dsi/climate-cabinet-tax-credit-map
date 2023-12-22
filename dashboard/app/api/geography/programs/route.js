/**
 * API route for tax credit program requests.
 */

"server only";

import prisma from "@/lib/db";
import { NextRequest, NextResponse } from "next/server";


/**
 * Fetches a summary of tax benefit programs for all geographies.
 *
 *  @param {NextRequest} - The HTTP request.
 */
export async function GET(request) {

  // Fetch all programs from database
  let data = await prisma.$queryRaw`
    SELECT * FROM tax_credit_program;`;

  // Manually correct JSONB columns (parsed by Prisma to have backticks)
  let mapped = data.map((r, _) => {
    let jsonb = r["bonus_amounts"]
    let parsed = JSON.parse(jsonb.substring(1, jsonb.length - 1))
    r["bonus_amounts"] = parsed
    return r
  });

  return NextResponse.json(mapped);
}
