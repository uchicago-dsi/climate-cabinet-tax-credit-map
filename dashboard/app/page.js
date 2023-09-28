/***
 * Renders a webpage for searching and viewing tax
 * credit benefit summaries for a geography.
 */

"use client";

import Autocomplete from "@/components/Autocomplete";
import ReportWidget from "@/components/ReportWidget";
import { headers } from "@/next.config";
import { get } from "lib/http";
import React, { useEffect, useState } from "react";

export default function SearchPage() {
  const [programs, setPrograms] = useState([]);

  useEffect(() => {
    const getPrograms = async () => {
      try {
        const url = `${process.env.NEXT_PUBLIC_DASHBOARD_BASE_URL}/api/geography/programs/`;
        const errMsg = `Failed to retrieve programs`;
        const response = await get(url, errMsg);
        console.log(response.data);
        setPrograms(response.data);
      } catch (error) {
        console.error("Failed to retrieve programs data", error);
      }
    };
    getPrograms();
  }, []);

  return (
    <div className="max-w-7xl mx-auto py-2">
      {/** HEADER  */}
      <div className="flex flex-col items-center">
        {/** TITLE BANNER */}
        <div
          className="w-screen py-12 bg-center bg-cover bg-no-repeat"
          style={{ backgroundImage: `url('/images/c3titlebanner2.jpg')` }}
        >
          <div className="container w-full max-w-fit mx-auto px-10">
            <h1 className="humani-title">
              Federal Funding Bonus Eligibility Map (beta)
            </h1>
          </div>
        </div>
        {/** DESCRIPTION */}
        <div className="max-w-5xl pt-12">
          <p>
            With this new tool from Climate Cabinet Education, discover which
            parts of your community have the potential to maximize the benefits
            of the historic federal climate investments from the Inflation
            Reduction Act. Areas meeting key eligibility criteria will qualify
            for greater even greater levels of funding.
          </p>
          <h5>Search for your community</h5>
          <p>
            Enter the name of a state, county, municipality, or rural electric
            cooperative to view its Justice 40 communities, energy communities,
            and designated low-income census tracts and MSAs on an interactive
            map. You’ll also see descriptions of which programs are available
            and how much bonus eligibility parts of your community can access.
          </p>
        </div>
        {/** AUTOCOMPLETE SEARCH BAR */}
        <div className="px-20 mt-10 mb-5 z-50 self-start w-11/12 mx-auto">
          <Autocomplete />
        </div>
      </div>
      {/** REPORT WIDGET */}
      <div>
        <ReportWidget />
      </div>
      <div className="flex flex-col items-center">
        <div className="max-w-5xl pt-12">
          <h3 className="text-center">Tax Credit Programs</h3>
          <table className="table-auto border-collapse w-full">
            <thead>
              <tr>
                <th className="px-4 py-2 border">Name</th>
                <th className="px-4 py-2 border">Agency</th>
                <th className="px-4 py-2 border">Description</th>
                <th className="px-4 py-2 border">Base Benefit</th>
              </tr>
            </thead>
            <tbody>
              {programs.map((program, index) => (
                <tr key={index}>
                  <td className="px-4 py-2 border">{program.name}</td>
                  <td className="px-4 py-2 border text-center">
                    {program.agency}
                  </td>
                  <td className="px-4 py-2 border">{program.description}</td>
                  <td className="px-4 py-2 border">{program.base_benefit}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* METHODOLOGY EXPLANATION */}
          <h3 className="text-center">Methodology</h3>
          <p>
            To estimate populations in specific geographic regions, we utilized
            the population-weighted centroid of Census Block Groups from the
            2020 United States Census. Block groups are subdivisions of census
            tracts, typically holding 600 to 3,000 people. Block groups allow
            for a more fine-grained approach to population estimates since
            population densities can vary within a single census tract.
          </p>
          <p>
            If a block group's population-weighted centroid fell within a
            particular geography, we attributed its entire population to that
            area. Both census tracts and block groups respect state and county
            boundaries. However, census tracts and block groups may cross zip
            codes, municipal utility, and/or rural cooperative boundaries.
          </p>
          <p>
            When estimating populations for intersecting areas — for example,
            the number of inhabitants in a Justice40 community served by
            Coles-Moultrie Electric Cooperative — we allocated the full
            population of any block groups whose population-weighted centroid
            was in the overlapping region. If the population-weighted centroid
            was not in the intersecting area, we did not allocate any of the
            population to the overlapping area.
          </p>
        </div>
      </div>
    </div>
  );
}
