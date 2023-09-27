/***
 * A parent container for a DeckGL map and legend.
 */

"use client";

import MapWidget from "@/components/MapWidget";
import SummaryStats from "@/components/SummaryStats";
import { reportStore } from "@/states/search";
import classNames from "classnames";
import { useSnapshot } from "valtio";

function ReportWidget() {
  const reportSnapshot = useSnapshot(reportStore);
  const targetGeo = reportSnapshot?.report?.geographies?.find(
    (m) => m.properties.is_target
  );

  return (
    <div className="px-20">
      <div className="flex w-full pt-10">
        <div className="grid grid-cols-8 m-0">
          {/** MAP */}
          <div className="col-span-6 border-8 border-ccblue-dark">
            <MapWidget />
          </div>
          {/** SUMMARY STATISTICS SIDEBAR */}
          <div
            className={
              "col-span-2 flex flex-col w-full h-[75vh] px-5 bg-white border-2 border-slate-100 text-xl overflow-y-auto scrollbar " +
              classNames({ "justify-center": !targetGeo })
            }
          >
            <SummaryStats />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportWidget;
