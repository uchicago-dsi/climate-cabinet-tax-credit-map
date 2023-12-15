/**
 * Summarizes population and tax credit program data for a geography.
 */

"use client";

import { reportStore } from "@/states/search";
import { useSnapshot } from "valtio";
import { layerConfig } from "@/config/layers";
import { layerStore } from "@/states/search";

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

    // TODO: this is kind of a hack
    this.programDict = {
      "distressed": {
        singular: "Distressed Community",
        plural: "Distressed Communities",
      },
      "energy": {
        singular: "Energy Community",
        plural: "Energy Communities",
      },
      "justice40": {
        singular: "Justice 40 Community",
        plural: "Justice 40 Communities",
      },
      "low-income": {
        singular: "Low Income Census Tract",
        plural: "Low Income Census Tracts",
      },
    };
    // Fill in any missing geography types
    Object.keys(this.programDict).forEach((prog) => {
      if (!this.summaryStats.hasOwnProperty(prog)) {
        this.summaryStats[prog] = {
          count: 0,
          population: 0,
        };
      } else {
        this.summaryStats[prog] = {
          ...this.summaryStats[prog],
          count: this.bonusDetails?.[prog]?.length ?? 0,
        };
      }
    });
  }

  // TODO: should probably remove these extra functions
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
      case "rural cooperative":
        return {
          single: "rural co-op",
          plural: "rural co-ops",
        };
      case "municipality":
          return {
            single: "municipality",
            plural: "municipalities",
          };
      case "municipal utility":
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
      case "low-income":
        return {
          single: "low income census tract",
          plural: "low income census tracts",
        };

      default:
        throw Error(`Received unexpected geography type ${rawType}.`);
    }
  }

  #groupBonusTerritories(geos) {
    let targetTypes = [
      "municipality", 
      "municipal utility", 
      "rural cooperative", 
      "county", 
      "state"
    ];
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
    for (const item of [
      "state", 
      "county", 
      "municipality", 
      "municipal_util", 
      "rural_coop"
    ]) {
      if (item in this.summaryStats) {
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

  // TODO: Not sure that this is the right spot to do this but setting default county visibility here
  const countySelected = builder.targetGeoType === "county";

  if (countySelected) {
    layerStore["Counties"].visible = true;
  } else {
    layerStore["Counties"].visible = false;
  }

  return (
    <div>
      <div>
        <div className="pt-5 pb-1">
          <h5 className="font-bold m-0 p-0 line-height[1]">
            {builder.targetFullName}{" "}
          </h5>
          <div>
            <span
              className="shadow-md no-underline rounded-full text-xs font-semibold p-2 uppercase m-0"
              style={{
                background: `rgb(${layerConfigObject[layerType].fillColor
                  .slice(0, 3)
                  .join(",")},${sideBarOpacity})`,
                color: ["rural_coop", "state", "municipal_util"].includes(
                  layerType
                )
                  ? "black"
                  : "white",
              }}
            >
              {builder.targetGeoType.replace("_", " ")}
            </span>
          </div>
        </div>
        <h6 className="pb-1">
          <b>Total Population</b>
          <br />
          {builder.targetPop}
          <br />
        </h6>
        <div>
          <h6 className="pb-1">
            <b>Bonus Territories</b>
            <p className="text-sm p-0">
              Populations are estimated in the overlap of your search area
              (state, county, municipal utility, or coop) and the bonus
              territories
            </p>
          </h6>
          <span>
            <ol className="text-sm">
              {Object.entries(builder.programDict).map(([key, value]) => (
                <li key={key} className="flex items-center">
                  <div
                    className="swatch"
                    style={{
                      background: `rgb(${layerConfigObject[key].fillColor
                        .slice(0, 3)
                        .join(",")},${sideBarOpacity})`,
                    }}
                  ></div>
                  <div>
                    <b className="mr-.5">{builder.summaryStats[key].count}</b>{" "}
                    {builder.summaryStats[key].count === 1
                      ? builder.programDict[key].singular
                      : builder.programDict[key].plural}{" "}
                    with{" "}
                    {(
                      Math.round(
                        (builder.summaryStats[key]?.population || 0) / 1000
                      ) * 1000
                    ).toLocaleString()}{" "}
                    people
                  </div>
                  <br />
                </li>
              ))}
            </ol>
          </span>
        </div>
        <div>
          <h6 className="pb-1">
            <b>Eligible Programs</b>
          </h6>
          <span>
            <ol className="list-disc text-sm">
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
