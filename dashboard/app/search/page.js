/***
 * Renders a webpage for searching and viewing tax
 * credit benefit summaries for a geography.
 */

"use client";

import Autocomplete from "@/components/Autocomplete";
import ReportWidget from "@/components/ReportWidget";

export default function SearchPage() {
  return (
    <div className="max-w-7xl mx-auto py-2">
      {/** HEADER  */}
      <div className="flex flex-col items-center">
        {/** TITLE BANNER */}
        <div
          className="w-screen py-10 bg-center bg-cover bg-no-repeat"
          style={{ backgroundImage: `url('/images/c3titlebanner2.jpg')` }}
        >
          <div className="container max-w-7xl mx-auto">
            <h1 className="humani-title">
              Federal Funding Bonus Eligibility Map (beta)
            </h1>
          </div>
        </div>
        {/** DESCRIPTION */}
        <div>
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
          {/* <p className="px-20 pt-8 text-lg">
                        Enter the name of a state, county, municipality or rural electric
                        cooperative to view its Justice 40 communities, energy communities,
                        and designated low-income census tracts and MSAs on an interactive
                        map. The sidebar will also show a description of available tax credit
                        programs.
                    </p> */}
        </div>
        {/** AUTOCOMPLETE SEARCH BAR */}
        <div className="px-20 mt-10 mb-5 z-50 self-start w-11/12">
          <Autocomplete />
        </div>
      </div>
      {/** REPORT WIDGET */}
      <div>
        <ReportWidget />
      </div>
    </div>
  );
}
