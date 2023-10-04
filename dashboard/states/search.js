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
let isVisible = layerConfig.reduce((acc, config) => {
    acc[config.id] = { visible: true, hasData: false };
    return acc;
}, {});
const layerStore = proxy(isVisible);

// Initialize search query store
const [searchStore] = useGeoSearch("");

// Initialize report store
const reportStore = proxy({
    report: null,
    status: null,
    setReport: (value) => reportStore.report = value,
})

// Subscribe to search store to update reports and map viewport
derive({
    fetchReports: (get) => {
        let geoId = get(searchStore).selected?.id;
        const status = reportStore.status;
        if (geoId && status !== `${geoId} loading` && status !== `${geoId} success`){
            reportStore.status = `${geoId} loading`;
            (getGeoReport(geoId)
                .then(r => {
                    reportStore.setReport(r);
                    viewportStore.zoomToGeography(r.geographies);
                    reportStore.status = `${geoId} success`;
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