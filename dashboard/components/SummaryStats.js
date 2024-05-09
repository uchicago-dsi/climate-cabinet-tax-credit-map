"use client";

/**
 * Summarizes population and tax credit program data for a geography.
 */

import { reportStore } from "@/states/search";
import { useSnapshot } from "valtio";
import { layerConfig, statsConfig } from "@/config/layers";

class SummaryBuilder {
  constructor(report) {
    // Set target geography fields
    let targetProps = report.target.properties;
    this.target = {
      name: targetProps.name,
      geoType: targetProps.geography_type,
      population: targetProps.population?.toLocaleString() ?? "Unknown",
      style: this.#getStyle(targetProps.geography_type),
    };

    // Set bonus geography fields
    this.bonuses = report.stats.map((stat) => {
      let roundedPop = Math.round((stat.population || 0) / 1000) * 1000;
      let config = statsConfig[stat.geography_type];
      return {
        entity: stat.count === 1 ? config.single : config.plural,
        count: stat.count.toLocaleString(),
        population: roundedPop.toLocaleString(),
        style: this.#getStyle(stat.geography_type),
      };
    });

    // Set program fields
    this.programs = report.programs;
  }

  #getStyle(geoType) {
    let layer = layerConfig.find((c) => c.externalId === geoType);
    return {
      background: `rgb(${layer.fillColor.slice(0, 3).join(",")},0.3)`,
      color: ["county", "municipality"].includes(geoType) ? "white" : "black",
    };
  }
}

function SummaryStats() {
  const reportSnap = useSnapshot(reportStore);
  if (reportSnap.report === null) {
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

  const summary = new SummaryBuilder(reportSnap.report);

  return (
    <div>
      <div>
        <div className="pt-5 pb-1">
          <h5 className="font-bold m-0 p-0 line-height[1]">
            {summary.target.name}{" "}
          </h5>
          <div>
            <span
              className="shadow-md no-underline rounded-full text-xs font-semibold p-2 uppercase m-0"
              style={summary.target.style}
            >
              {summary.target.geoType}
            </span>
          </div>
        </div>
        <h6 className="pb-1">
          <b>Total Population (2020)</b>
          <br />
          {summary.target.population}
          <br />
        </h6>
        <div>
          <h6 className="pb-1">
            <b>Bonus Territories</b>
            <p className="text-sm p-0">
              Populations are estimated in the overlap of your search area
              (state, county, municipal utility, or rural co-op) and the bonus
              territories and then rounded to the nearest thousand.
            </p>
          </h6>
          <span>
            <ol className="text-sm">
              {summary.bonuses.map((bonus, idx) => (
                <li key={idx} className="flex items-center">
                  <div
                    className="swatch"
                    style={{ background: bonus.style.background }}
                  ></div>
                  <div>
                    <b className="mr-.5">{bonus.count}</b>{" "}
                    {`${bonus.entity} with ${bonus.population} people.`}
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
              {summary.programs.map((program, idx) => {
                return <li key={idx}>{program}</li>;
              })}
            </ol>
          </span>
        </div>
      </div>
    </div>
  );
}

export default SummaryStats;
