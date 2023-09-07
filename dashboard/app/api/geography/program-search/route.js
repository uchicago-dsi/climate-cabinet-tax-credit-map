/**
 * API route for tax credit program search requests.
 */

"server only"

import prisma from "@/lib/db";
import { NextRequest, NextResponse } from 'next/server';
import { Prisma } from '@prisma/client';


/**
 * Fetches a summary of tax benefit programs
 * for one or more geographies.
 * 
 *  @param {NextRequest} - The HTTP request. Contains an array of geography ids.
 */
export async function POST(request) {
  let { geometryIds } = await request.json();
  let data = await prisma.$queryRaw`
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
    WHERE geo.id IN (${Prisma.join(geometryIds)});`;
  return NextResponse.json({ data })
}
