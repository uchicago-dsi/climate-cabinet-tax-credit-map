/***
 * A parent container for a DeckGL map and legend.
 */

"use client";

import MapWidget from "@/components/MapWidget";
import SummaryStats from "@/components/SummaryStats";
import { reportStore } from "@/states/search";
import { useSnapshot } from "valtio";

function ReportWidget({ programs }) {
  const reportSnapshot = useSnapshot(reportStore);
  const targetGeo = reportSnapshot?.report?.geographies?.find(
    (m) => m.properties.is_target
  );

  return (
    <div className="px-4">
      <div
        className="grid grid-cols-1 md:grid-cols-8 m-0 min-h-[600px] pt-10"
        id="report-widget"
      >
        {/** MAP */}
        <div className="md:col-span-6 col-span-1 border-8 m-0 min-h-[75vh] border-ccblue-dark">
          <MapWidget />
        </div>
        {/** SUMMARY STATISTICS SIDEBAR */}
        <div
          className={`md:col-span-2 col-span-1 flex flex-col w-full h-full px-5 m-0 bg-white border-2 border-slate-100 text-xl overflow-y-auto scrollbar min-h-[600px] ${
            !targetGeo ? "justify-center" : ""
          }`}
        >
          <SummaryStats programs={programs} />
        </div>
      </div>
    </div>
  );
}

export default ReportWidget;
