/***
 * Renders a webpage for searching and viewing tax
 * credit benefit summaries for a geography.
 */

"use client";

import Autocomplete from "@/components/Autocomplete";
import Link from "@/components/Link";
import ReportWidget from "@/components/ReportWidget";
import { get } from "lib/http";
import React, { useEffect, useState } from "react";
import { layerConfig } from "@/config/layers";
import { capitalize } from "lodash";

export default function SearchPage() {
  const [programs, setPrograms] = useState([]);

  useEffect(() => {
    const getPrograms = async () => {
      try {
        const url = `${process.env.NEXT_PUBLIC_DASHBOARD_BASE_URL}/api/geography/programs/`;
        const errMsg = `Failed to retrieve programs`;
        const data = await get(url, errMsg);
        setPrograms(data);
      } catch (error) {
        console.error("Failed to retrieve programs data", error);
      }
    };
    getPrograms();
  }, []);

  const formatBonusDescription = (obj) => {
    return Object.entries(obj).map(([key, val], _) => {
      let config = layerConfig.find((c) => c.externalId === key);
      return { title: config.id, description: capitalize(val) };
    });
  };

  return (
    <div className="max-w-7xl mx-auto py-2 px-2">
      {/** HEADER  */}
      <div className="flex flex-col items-center">
        {/** TITLE BANNER */}
        {/* <div
          className="w-screen py-12 bg-center bg-cover bg-no-repeat"
          style={{ backgroundImage: `url('/images/c3titlebanner2.jpg')` }}
        >
          <div className="container w-full max-w-fit mx-auto px-10">
            <h1 className="humani-title text-center sm:text-left">
              Federal Funding Bonus Eligibility Map (beta)
            </h1>
          </div>
        </div> */}
        {/** DESCRIPTION */}
        {/* <div className="max-w-5xl pt-12">
          <p>
            With this new tool from Climate Cabinet Education, discover which
            parts of your community have the potential to maximize the benefits
            of the historic federal climate investments from the Inflation
            Reduction Act. Areas meeting key eligibility criteria will qualify
            for even greater levels of funding.
          </p>
          <h5>Search for your community</h5>
          <p>
            Enter the name of a state, county, municipal utility, or rural
            electric cooperative to view its Justice40 communities, distressed
            zip codes, energy communities, and designated low-income census
            tracts on an interactive map. You'll also see descriptions of which
            programs are available and how much bonus eligibility parts of your
            community can access.
          </p>
        </div> */}
        {/** AUTOCOMPLETE SEARCH BAR */}
        <div className="px-2 sm:px-20 mt-10 mb-5 z-50 self-start w-11/12 mx-auto max-h-[200px]">
          <Autocomplete />
        </div>
      </div>
      {/** REPORT WIDGET */}
      <div>
        <ReportWidget programs={programs} />
      </div>
      {/* <div className="flex flex-col items-center">
        <div className="max-w-5xl pt-12 overflow-x-auto">
          <h3 className="text-center pt-10 font-bold">Tax Credit Programs</h3>
          <hr />
          <table className="table-auto border-collapse w-full">
            <thead>
              <tr>
                <th className="px-4 py-2 border">Name</th>
                <th className="px-4 py-2 border">Agency</th>
                <th className="px-4 py-2 border hidden sm:table-cell">
                  Description
                </th>
                <th className="px-4 py-2 border">Base Benefit</th>
                <th className="px-4 py-2 border hidden sm:table-cell">
                  Bonus Amounts
                </th>
              </tr>
            </thead>
            <tbody>
              {programs.map((program, index) => (
                <tr key={index}>
                  <td className="px-4 py-2 border">{program.name}</td>
                  <td className="px-4 py-2 border text-center">
                    {program.agency.replace("nan", "---")}
                  </td>
                  <td className="px-4 py-2 border hidden sm:table-cell">
                    {program.description}
                  </td>
                  <td className="px-4 py-2 border">{program.base_benefit}</td>
                  <td
                    className="px-4 py-2 border hidden sm:table-cell"
                    style={{ whiteSpace: "pre-line" }}
                  >
                    {program.bonus_amounts &&
                      formatBonusDescription(program.bonus_amounts).map(
                        (obj, idx) => {
                          return (
                            <p key={idx}>
                              <span className="font-bold">{obj.title}:</span>{" "}
                              {obj.description}
                            </p>
                          );
                        }
                      )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table> */}

      {/* DATA DESCRIPTION */}
      {/* <h3 className="text-center pt-10 font-bold">Data</h3>
          <hr /> */}

      {/* ADMINISTRATIVE BOUNDARIES */}
      {/* <h4>Administrative Boundaries</h4>
          <p>
            Boundaries for counties, states, zip codes, and U.S. territories
            were extracted from TIGER/Line Shapefiles corresponding to the 2020
            U.S. Census. The data may be accessed through the U.S. Census
            Bureau's{" "}
            <Link
              url="https://www.census.gov/cgi-bin/geo/shapefiles/index.php"
              text="web tool"
            />{" "}
            or{" "}
            <Link
              url="https://www2.census.gov/geo/tiger/TIGER2020/TRACT/"
              text="FTP server"
            />
            .
          </p> */}

      {/* DISTRESSED COMMUNITIES */}
      {/* <h4>Distressed Communities</h4>
          <p>
            Distressed zip codes were obtained by downloading and filtering a
            CSV data file from the latest release of the Economic Innovation
            Group's{" "}
            <Link
              url="https://eig.org/distressed-communities/"
              text="Distressed Communities Index (DCI)"
            />
            . The release uses the U.S. Census Bureau's Business Patterns and
            American Community Survey 5-Year Estimates for 2016-2020. Zip codes
            identified as "distressed" by EIG were then merged with 2020
            TIGER/Line zip code Shapefiles from the U.S. Census Bureau to
            produce the final dataset.
          </p> */}

      {/* ELECTRIC UTILITIES */}
      {/* <h4>Electric Retail Service Territories</h4>
          <p>
            Shapefiles for rural cooperatives and municipal utilities were
            downloaded from the Homeland Infrastructure Foundation-Level Data
            (HIFLD){" "}
            <Link
              url="https://hifld-geoplatform.opendata.arcgis.com/"
              text="open data portal"
            />
            , hosted by the Geospatial Management Office of the U.S. Department
            of Homeland Security. The data, which may also be viewed on an{" "}
            <Link
              url="https://hifld-geoplatform.opendata.arcgis.com/datasets/electric-retail-service-territories-2/explore?showTable=true"
              text="alternative web map"
            />
            , was last published on December 9, 2022, and utilizes multiple data
            sources from different years (e.g., state GIS portals, Energy
            Information Administration Tiger/Line Shapefiles).
          </p> */}

      {/** ENERGY COMMUNITIES */}
      {/* <h4>Energy Communities</h4>
          <p>
            Two datasets for coal closure and fossil fuel employment qualifying
            energy communities were downloaded from the{" "}
            <Link
              url="https://edx.netl.doe.gov/dataset/ira-energy-community-data-layers"
              text="Energy Data eXchange"
            />
            , hosted by the Department of Energy's National Energy Technology
            Laboratory (NETL). The data was last updated on June 15, 2023. At
            present, two categories of energy communities under the Inflation
            Reduction Act (IRA) have been made publicly available through the
            platform:
          </p>
          <p className="pl-10 pr-10">
            1. Census tracts and directly adjoining tracts that have had coal
            mine closures since 1999 or coal-fired electric generating unit
            retirements since 2009.
          </p>
          <p className="pl-10 pr-10">
            2. Metropolitan statistical areas (MSAs) and non-metropolitan
            statistical areas (non-MSAs) that have had for at least one year
            since 2009, 0.17% or greater direct employment related to
            extraction, processing, transport, or storage of coal, oil, or
            natural gas (the fossil fuel employment (FFE) threshold){" "}
            <span className="font-bold">and</span> have an unemployment rate for
            2022 that is equal to or greater than the national average
            unemployment rate for 2022.
          </p>
          <p>
            The coal closure and FFE-eligible datasets were downloaded as zipped
            Shapefiles, filtered to include only geographies qualifying as
            energy communities, and then merged together to create the final
            dataset.
          </p> */}

      {/** JUSTICE40 COMMUNITIES */}
      {/* <h4>Justice40 Communities</h4>
          <p>
            A Shapefile containing metadata and geographic boundaries for
            Justice40 Communities was directly downloaded from the{" "}
            <Link
              url="https://screeningtool.geoplatform.gov/en/"
              text="Climate & Economic Justice Screening Tool (v.1)"
            />
            , last updated on November 22, 2022. The Council on Environmental
            Quality, Executive Office of the President, which manages the tool,
            used 2010 census tracts for boundaries and 2015-2019 American
            Community Survey (ACS) demographic data to determine which tracts
            were classified as "disadvantaged" for at least one of eight
            criteria: climate change, energy, health, housing, legacy pollution,
            transportation, water and wastewater, and workforce development.
          </p> */}

      {/** LOW-INCOME COMMUNITIES */}
      {/* <h4>Low-Income Communities</h4>
          <p>
            According to statute (
            <Link
              url="https://www.govinfo.gov/content/pkg/USCODE-2010-title26/pdf/USCODE-2010-title26-subtitleA-chap1-subchapA-partIV-subpartD-sec45D.pdf"
              text="26 USC §45D(e)"
            />
            ), low-income communities (LICs) are defined as: "any population
            census tract if— '(A) the poverty rate for such tract is at least 20
            percent, or '(B)(i) in the case of a tract not located within a
            metropolitan area, the median family income for such tract does not
            exceed 80 percent of statewide median family income, or '(ii) in the
            case of a tract located within a metropolitan area, the median
            family income for such tract does not exceed 80 percent of the
            greater of statewide median family income or the metropolitan area
            median family income. Subparagraph (B) shall be applied using
            possessionwide median family income in the case of census tracts
            located within a possession of the United States."
          </p>
          <p>
            To identify low-income census tracts for the web map, an{" "}
            <Link
              url="https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/decision-support/mapping-low-income-communities-in-the-us/"
              text="analysis conducted by ESRI"
            />{" "}
            was replicated. TIGER/Line Shapefiles (2020) for nationwide census
            tracts were downloaded from the U.S. Census Bureau's web server and
            and 2016-2020 American Community Survey data was exported from
            Social Explorer for tables "B17020: Poverty Status in the Past 12
            Months" and "Table B19113: Median Family Income in the Past 12
            Months (in 2020 inflation-adjusted dollars)" at the tract,
            metropolitan statistical area, and state geography levels. A Python
            script was then executed to merge and filter the data to produce the
            final dataset.
          </p> */}

      {/* METHODOLOGY EXPLANATION */}
      {/* 
          <h3 className="text-center pt-10 font-bold">Methodology</h3>
          <hr />
          <p>
            To estimate populations in specific geographic regions, we utilized
            the population-weighted centroids of Census Block Groups from the
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
          <p>
            We compared two different methodologies for calculating population using
            census block groups. In one methodology, we calculated the percentage area 
            of a block group that intersected with a specific geography, and we 
            allocated that percentage of the block group's population to that geography.
            In the other methodology, we allocated the entire population of a block group 
            to a specific geography if the population-weighted centroid was inside of 
            that geography. The area allocated population methodology is much more 
            computationally expensive than the population-weighted centroid methodology.
          </p>
          <p>
            To test the difference between the two methodologies, we used a paired 
            T-test with 1,100 samples. To pick our sample size, we used an estimated 
            effect size of 0.1, a significance level of 0.05, and a power of 0.9. The 
            T-statistic was -0.36 and the p-value was 0.72, which indicates that 
            the differences in methodologies are not statistically significant. 
            Based on this, we used the less computationally expensive 
            population-weighted centroid methodology.
          </p>
        </div>
      </div>  */}
    </div>
  );
}
