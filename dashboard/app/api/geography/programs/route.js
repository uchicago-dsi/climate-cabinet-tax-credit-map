/**
 * API route for tax credit program search requests.
 */

"server only";

import prisma from "@/lib/db";
import { NextRequest, NextResponse } from "next/server";
import { Prisma } from "@prisma/client";

/**
 * Fetches a summary of tax benefit programs
 * for one or more geographies.
 *
 *  @param {NextRequest} - The HTTP request. Contains an array of geography ids.
 */
export async function GET(request) {
  let data = await prisma.$queryRaw`
    SELECT * FROM tax_credit_programs_updated;`;
  return NextResponse.json({ data });
}
