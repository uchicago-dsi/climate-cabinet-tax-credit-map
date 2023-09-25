/**
 * Summarizes population and tax credit program data for a geography.
 */

"use client";

import { reportStore } from "@/states/search";
import { useSnapshot } from "valtio";

class SummaryBuilder {
  #target;
  #bonusGrps;
  #programGrps;

  constructor(report) {
    let geos = report.geographies;
    let programs = report.programs;

    this.#target = geos.find((g) => g.properties.is_target).properties;
    this.#bonusGrps = this.#groupBonusTerritories(geos);
    this.#programGrps = this.#groupPrograms(programs);
  }

  #formatNum(num) {
    let under10 = [
      "zero",
      "one",
      "two",
      "three",
      "four",
      "five",
      "six",
      "seven",
      "eight",
      "nine",
    ];
    if (num < 10) return under10[num];
    return num.toLocaleString("en-US");
  }

  #getFormalGeoType(rawType) {
    switch (rawType) {
      case "state":
        return {
          single: "state",
          plural: "states",
        };
      case "county":
        return {
          single: "county",
          plural: "counties",
        };
      case "rural_coop":
        return {
          single: "rural co-op",
          plural: "rural co-ops",
        };
      case "municipal_util":
        return {
          single: "municipal utility",
          plural: "municipal utilities",
        };
      case "distressed":
        return {
          single: "distressed zip code",
          plural: "distressed zip codes",
        };
      case "energy":
        return {
          single: "energy community",
          plural: "energy communities",
        };
      case "justice40":
        return {
          single: "Justice 40 census tract",
          plural: "Justice 40 census tracts",
        };
      case "low_income":
        return {
          single: "low income census tract",
          plural: "low income census tracts",
        };

      default:
        throw Error(`Received unexpected geography type ${rawType}.`);
    }
  }

  #groupBonusTerritories(geos) {
    let targetTypes = ["municipal_util", "rural_coop", "county", "state"];
    return geos.reduce((grp, geo) => {
      let key = geo.properties.geography_type;
      if (targetTypes.includes(key)) return grp;
      grp[key] = grp[key] ?? [];
      grp[key].push(geo.properties);
      return grp;
    }, {});
  }

  #groupPrograms(programs) {
    return programs
      .toSorted((a, b) => (a.program_name < b.program_name ? -1 : 1))
      .reduce((grp, prog) => {
        let key = prog.program_name;
        let initial = {
          name: key,
          agency: prog.program_agency === "nan" ? "N/A" : prog.program_agency,
          description: prog.program_description,
          baseBenefit: prog.program_base_benefit,
          geoBenefits: [],
        };
        grp[key] = grp[key] ?? initial;
        grp[key].geoBenefits.push({
          geoType: this.#getFormalGeoType(prog.geography_type).single,
          additionalAmount: prog.program_amount_description,
        });
        return grp;
      }, {});
  }

  #describeBonusDems(bonusGeos, singleType, pluralType) {
    if (bonusGeos.length === 0) return "";
    let typeName = bonusGeos.length === 1 ? singleType : pluralType;
    let numGeos = bonusGeos.length.toLocaleString("en-US");
    let totalPop = bonusGeos.reduce((acc, li) => acc + li.total_population, 0);
    return (
      `${this.#formatNum(numGeos)} ${typeName} with a ` +
      `total population of ${this.#formatNum(totalPop)}`
    );
  }

  get targetGeoType() {
    return this.#getFormalGeoType(this.#target.geography_type).single;
  }

  get targetFullName() {
    if (this.#target.geography_type === "county") {
      return `${this.#target.name},`;
    }
    let geoType = this.targetGeoType;
    return (
      `${geoType.charAt(0).toUpperCase()}${geoType.slice(1)}` +
      ` ${this.#target.name}`
    );
  }

  get targetPop() {
    if (!this.#target.total_population) return "Unknown";
    return this.#target.total_population.toLocaleString("en-US");
  }

  get bonusDescription() {
    let clauses = Object.entries(this.#bonusGrps).map((entry) => {
      let [key, grp] = entry;
      let { single, plural } = this.#getFormalGeoType(key);
      return this.#describeBonusDems(grp, single, plural);
    });

    if (!clauses.length) {
      return "";
    } else if (clauses.length === 1) {
      return `It intersects with ${clauses[0]}.`;
    } else if (clauses.length === 2) {
      return `It intersects with ${clauses[0]} and ${clauses[1]}.`;
    } else {
      return (
        "It intersects with " +
        clauses.slice(0, clauses.length - 1).join("; ") +
        `; and ${clauses[clauses.length - 1]}.`
      );
    }
  }

  get bonusDetails() {
    return this.#bonusGrps;
  }

  get programDetails() {
    return this.#programGrps;
  }
}

function SummaryStats() {
  const reportSnap = useSnapshot(reportStore);

  if (!reportSnap.report?.geographies) {
    return (
      <div className="text-slate-400 font-medium text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={0.5}
          stroke="gray"
          className="w-12 h-12 block m-auto"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        No geographies selected.
      </div>
    );
  }

  const builder = new SummaryBuilder(reportSnap.report);

  return (
    <div>
      <div>
        <h3 className="font-bold">Summary</h3>
        <h4>
          <b>Total Population</b>
          <br />
          {builder.targetPop}
          <br />
        </h4>
        <div>
          <h4>
            <b>Bonus Territories</b>
          </h4>
          <span>
            <ol className="list-disc">
              <li>
                Distressed Zip Codes (
                {builder.bonusDetails?.distressed?.length ?? 0})<br />
              </li>
              <li>
                Energy Communities ({builder.bonusDetails?.energy?.length ?? 0})
              </li>
              <li>
                Justice 40 Census Tracts (
                {builder.bonusDetails?.justice40?.length ?? 0})
              </li>
              <li>
                Low Income Census Tracts (
                {builder.bonusDetails?.low_income?.length ?? 0})
              </li>
            </ol>
          </span>
        </div>
        <div>
          <h4>
            <b>Eligible Programs</b>
          </h4>
          <span>
            <ol className="list-disc">
              {Object.entries(builder.programDetails).map((entry, idx) => {
                let [_, prog] = entry;
                return <li>{prog.name}</li>;
              })}
            </ol>
          </span>
        </div>
      </div>
      {/* MOVE ALL OF THIS STUFF OUT OF SUMMARY STATS */}
      {/* <div>
        <h3 className="font-bold">Demographics</h3>
        <p>
          <b>{builder.targetFullName}</b> has an estimated total 
          population of{" "}{builder.targetPop} according 
          to the 2015-2019 American Community Survey.*{" "}
          {builder.bonusDescription}
        </p>
      </div>
      <div className="py-3">
        <h3 className="font-bold">Eligible Programs</h3>
        <p>
          Based on the tax credit bonus areas present in the{" "}
          {builder.targetGeoType}, the following programs are available:
        </p>
        {
          Object.entries(builder.programDetails)
            .map((entry, idx) => {
              let [_, prog] = entry;
              return (
                <div key={idx}>
                  <b>{prog.name} ({prog.agency})</b><br />
                  <span className="text-slate-400 italic">
                    Eligible based on presence of{" "}
                    {prog.geoBenefits.map(g => g.geoType).join(", ")}
                  </span>
                  <p>
                    <ol className="list-disc">
                      <li>
                        Base Benefit - {prog.baseBenefit}
                      </li>
                      {prog.geoBenefits.map(b => {
                        return (
                          <li key={b}>
                            {
                              b.geoType
                                .split(" ")
                                .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                                .join(" ")
                            }
                            {" "}Bonus Amount/Comment -{" "}
                            {
                              b.additionalAmount.charAt(0).toUpperCase() +
                              b.additionalAmount.slice(1)
                            }
                          </li>
                        );
                      })}
                    </ol>
                  </p>
                  <p>{prog.description}</p>
                </div>
              );
          })}
      </div> */}
    </div>
  );
}

export default SummaryStats;
