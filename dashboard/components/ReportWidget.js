/***
 * A parent container for a DeckGL map and legend.
 */

"use client"

import MapWidget from '@/components/MapWidget';
import { Suspense, useEffect, useState } from "react";
import { useGeoReport } from '@/hooks/useGeoReport';
import { useSnapshot } from "valtio";
import { get } from "@/lib/utils";


function ReportWidget({ geoId }) {

    const [report, setReport] = useState(null);

    useEffect(()=> {
        console.log("fetching")
        const getGeographyReport = async (geographyId) => {
            if (!geographyId) return null
            const url = `${process.env.NEXT_PUBLIC_DASHBOARD_BASE_URL}/api/geography/report/${geographyId}`;
            const errMsg = `Failed to retrieve report for geography ${geographyId}.`;
            return await get(url, errMsg);
        }
        getGeographyReport(geoId).then(report => setReport(report));
    }, [geoId])


    return (
        <Suspense fallback={<h1>Is Loading</h1>}>
            <div className="flex w-full px-20" style={{ paddingTop: 20 }}>
                {/** MAP */}
                <MapWidget geographies={report} />
                
                {/** SIDEBAR */}
                {/* <div className="grid grid-cols-8" style={{backgroundColor: "yellow"}}>
                <h2>Summary Stats</h2>
            </div> */}

                {/* <div className="flex flex-col w-1/4 h-[75vh] overflow-hidden px-5">
                <SummaryStats />
            </div> */}
            </div>
        </Suspense>
    );
}

export default ReportWidget;