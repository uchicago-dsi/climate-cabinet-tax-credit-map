/**
 * A custom hook to fetch a report for a geography.
 */

"server only"

import { get } from "@/lib/http";


function getGeoReport(geoId) {

    /**
     * A private function to fetch a report for a geography.
     * 
     * @param {*} geoId 
     * @returns An object representing the report.
     */
    const _getGeographyReport = (geoId) => {
        if (!geoId) return null
        const url = `${process.env.NEXT_PUBLIC_DASHBOARD_BASE_URL}/api/geography/report/${geoId}`;
        const errMsg = `Failed to retrieve report for geography ${geoId}.`;
        return get(url, errMsg);
    }

    return _getGeographyReport(geoId);
}

export { getGeoReport };
