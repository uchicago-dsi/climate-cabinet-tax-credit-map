/***
 * A parent container for a DeckGL map and control panel.
 */

"use client";

import 'mapbox-gl/dist/mapbox-gl.css';
import Banner from "@/components/Banner";
import DeckGL from "@deck.gl/react";
import MapControlPanel from "@/components/MapControlPanel";
import Tooltip from "@/components/Tooltip";
import { Map } from "react-map-gl";
import { useSnapshot } from "valtio";
import { Suspense } from "react";
import {
  reportStore,
  baseMapStore,
  viewportStore,
  layerStore,
} from "@/states/search";
import { useLayers } from "@/hooks/useLayers";


function MapWidget() {
    const reportSnap = useSnapshot(reportStore);
    const baseMapSnap = useSnapshot(baseMapStore);
    const layerSnap = useSnapshot(layerStore);
    const layerClient = useLayers(reportSnap.report?.geographies, layerStore);

    return (
        <div 
            className="relative overflow-hidden" 
            style={{width: "100%", height: "100%"}}
        >
            <Suspense fallback={<Banner notificationText={"Loading geographies..."} />}>
            <DeckGL
                layers={Object.entries(layerSnap).reduce((layers, [id, state]) => {
                        if (state.visible) {
                            let lyr = layerClient.getLayer(id);
                            layers.push(lyr);
                        }
                        return layers;
                }, [])}
                initialViewState={viewportStore.current}
                controller={true}
            >
                <Map
                    mapStyle={baseMapSnap.selected.url}
                    mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN}
                />
            </DeckGL>
            {/* TODO: add a picking radius here to layers?*/}
              <Tooltip />
            <div className="absolute right-4 top-4 bg-white p-2">
                <MapControlPanel 
                    baseMapSnap={baseMapSnap}
                    reportSnap={reportSnap.report}
                    layerStore={layerStore}
                />
            </div>
            </Suspense>
        </div>
    );
}

export default MapWidget;
