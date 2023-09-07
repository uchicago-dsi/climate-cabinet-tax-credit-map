/**
 * A custom hook to fetch a report for a geography.
 */

"server only"

import { get } from "@/lib/utils";
import { proxy } from "valtio";
import { derive } from "valtio/utils";


function useGeoReport(initialGeographyId) {

    /**
     * A private function to fetch a report for a geography.
     * 
     * @param {*} geographyId 
     * @returns An object representing the report.
     */
    const _getGeographyReport = async (geographyId) => {
        if (!geographyId) return null
        const url = `${process.env.NEXT_PUBLIC_DASHBOARD_BASE_URL}/api/geography/report/${geographyId}`;
        const errMsg = `Failed to retrieve report for geography ${geographyId}.`;
        return await get(url, errMsg);
    }

    // Define state variables
    const state = proxy({
        // geoId: initialGeographyId,
        // setGeoId: (value) => state.geoId = value,
        report: (geoId) => _getGeographyReport(geoId).then(r => r)
    });


    return [ state ]
}

export { useGeoReport };
