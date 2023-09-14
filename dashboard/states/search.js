/**
 * Maintains global state for the tax credit bonus territory search page.
 */

"server only"

import { layerConfig } from "@/config/layers";
import { proxy } from "valtio";
import { getGeoReport } from "@/hooks/useGeoReport";
import { useGeoSearch } from "@/hooks/useGeoSearch";
import { useBaseMapStore } from "@/hooks/useBaseMapStore";
import { useViewportStore } from "@/hooks/useViewportStore";
import { derive } from "valtio/utils";

// Initialize deck.gl base map store
const baseMapStore = useBaseMapStore();

// Initialize deck.gl viewport store
const viewportStore = useViewportStore();

// Initialize deck.gl layer visiblity store
let isVisibleKvps = layerConfig.map(config => [
    config.id, { visible: true, hasData: false }
]);
const layerStore = proxy(Object.fromEntries(isVisibleKvps));

// Initialize search query store
const [searchStore] = useGeoSearch("");

// Initialize report store
const reportStore = proxy({
    report: null,
    setReport: (value) => reportStore.report = value,
})

// Subscribe to search store to update reports and map viewport
derive({
    fetchReports: (get) => {
        let geoId = get(searchStore).selected?.id;
        let prevQuery = get(searchStore).selected?.name;
        let currentQuery = get(searchStore).query;

        if (geoId && prevQuery == currentQuery){
            (getGeoReport(geoId)
                .then(r => {
                    get(reportStore).setReport(r);
                    get(viewportStore).zoomToGeography(r);
                }))
        }
    }
});

export {
    searchStore,
    reportStore,
    baseMapStore,
    viewportStore,
    layerStore
}