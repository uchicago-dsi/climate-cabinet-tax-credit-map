/**
 * Summarizes population and tax credit program data for a geography.
 */

"use client";

import { reportStore } from "@/states/search";
import { useSnapshot } from "valtio";
import { layerConfig } from "@/config/layers";

class SummaryBuilder {
  #target;
  #bonusGrps;
  #programGrps;

  constructor(report) {
    let geos = report.geographies;
    let programs = report.programs;

    this.summaryStats = {};

    JSON.parse(report.summaryStats).forEach((item) => {
      let key = item.type;
      this.summaryStats[key] = {
        ...this.summaryStats[key],
        population: parseInt(item.population, 10),
      };
    });

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

  get targetGeoTypeRaw() {
    return this.#target.geography_type;
  }

  get targetFullName() {
    return `${this.#target.name}`;
  }

  get targetPop() {
    for (const item of ["state", "county", "municipal_util", "rural_coop"]) {
      if (item in this.summaryStats) {
        console.log(
          "In the target pop builder",
          this.summaryStats[item].population
        );
        return this.summaryStats[item].population.toLocaleString();
      }
    }
    return "Unknown";
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

  const layerConfigObject = {};

  layerConfig.forEach((layer) => {
    layerConfigObject[layer.externalId] = layer;
  });

  const layerType = builder.targetGeoTypeRaw;
  const sideBarOpacity = 0.3;

  console.log("summaryStats", builder.summaryStats);
  console.log("targetPop", builder.targetPop);

  return (
    <div>
      <div>
        <h5 className="font-bold m-0 pt-5 pb-1">{builder.targetFullName} </h5>
        <span
          className="shadow-md no-underline rounded-full text-xs font-semibold p-2 uppercase"
          style={{
            background: `rgb(${layerConfigObject[layerType].fillColor
              .slice(0, 3)
              .join(",")},${sideBarOpacity})`,
            color: ["rural_coop", "state", "municipal_util"].includes(layerType)
              ? "black"
              : "white",
          }}
        >
          {builder.targetGeoType.replace("_", " ")}
        </span>
        <h6 className="pb-1">
          <b>Total Population</b>
          <br />
          {builder.targetPop}
          <br />
        </h6>
        <div>
          <h6 className="pb-1">
            <b>Bonus Territory Counts</b>
          </h6>
          <span>
            <ol className="text-sm">
              <li className="flex items-center">
                <div
                  className="swatch"
                  style={{
                    background: `rgb(${layerConfigObject["distressed"].fillColor
                      .slice(0, 3)
                      .join(",")},${sideBarOpacity})`,
                  }}
                ></div>
                <b className="mr-1">
                  {builder.bonusDetails?.distressed?.length ?? 0}
                </b>{" "}
                Distressed Zip Codes with{" "}
                {(
                  Math.round(
                    (builder.summaryStats["distressed"]?.population || 0) / 1000
                  ) * 1000
                ).toLocaleString()}{" "}
                <br />
              </li>
              <li className="flex items-center">
                <div
                  className="swatch"
                  style={{
                    background: `rgb(${layerConfigObject["energy"].fillColor
                      .slice(0, 3)
                      .join(",")},${sideBarOpacity})`,
                  }}
                ></div>
                <b className="mr-1">
                  {builder.bonusDetails?.energy?.length ?? 0}
                </b>{" "}
                Energy Communities
              </li>
              <li className="flex items-center">
                <div
                  className="swatch"
                  style={{
                    background: `rgb(${layerConfigObject["justice40"].fillColor
                      .slice(0, 3)
                      .join(",")},${sideBarOpacity})`,
                  }}
                ></div>
                <b className="mr-1">
                  {builder.bonusDetails?.justice40?.length ?? 0}
                </b>{" "}
                Justice 40 Census Tracts
              </li>
              <li className="flex items-center">
                <div
                  className="swatch"
                  style={{
                    background: `rgb(${layerConfigObject["low_income"].fillColor
                      .slice(0, 3)
                      .join(",")},${sideBarOpacity})`,
                  }}
                ></div>
                <b className="mr-1">
                  {builder.bonusDetails?.low_income?.length ?? 0}
                </b>{" "}
                Low Income Census Tracts
              </li>
            </ol>
          </span>
        </div>
        <div>
          <h6 className="pb-1">
            <b>Eligible Programs</b>
          </h6>
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
    </div>
  );
}

export default SummaryStats;
