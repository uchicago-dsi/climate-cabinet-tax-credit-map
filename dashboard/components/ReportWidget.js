/***
 * A parent container for a DeckGL map and legend.
 */

"use client"

import MapWidget from "@/components/MapWidget";
import SummaryStats from "@/components/SummaryStats";


function ReportWidget() {

    return (
        <div className="flex w-full px-20" style={{ paddingTop: 20 }}>
            <div className="grid grid-cols-8 m-0 p-0">
                {/** MAP */}
                <div className="col-span-6">
                    <MapWidget />
                </div>
                {/** SUMMARY STATISTICS SIDEBAR */}
                <div className="col-span-2 flex flex-col w-full h-[75vh] px-5 bg-white border-2 border-slate-100">
                    <SummaryStats />
                </div>
            </div>
        </div>
    );
}

export default ReportWidget;