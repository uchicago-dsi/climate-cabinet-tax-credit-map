/***
 * A parent container for a DeckGL map and legend.
 */

"use client"

import MapWidget from '@/components/MapWidget';


function ReportWidget() {

    return (
        <div className="flex w-full px-20" style={{ paddingTop: 20 }}>
            {/** MAP */}
            <MapWidget />
            
            {/** SIDEBAR */}
            {/* <div className="grid grid-cols-8" style={{backgroundColor: "yellow"}}>
            <h2>Summary Stats</h2>
        </div> */}

            {/* <div className="flex flex-col w-1/4 h-[75vh] overflow-hidden px-5">
            <SummaryStats />
        </div> */}
        </div>
    );
}

export default ReportWidget;