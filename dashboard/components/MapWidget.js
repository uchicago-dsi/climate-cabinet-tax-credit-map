/***
 * A parent container for a DeckGL map and control panel.
 */

"use client";

import DeckGL from "@deck.gl/react";
import MapControlPanel from "@/components/MapControlPanel";
import { Map } from "react-map-gl";
import { useMap } from "@/hooks/useMap";
import { useSnapshot } from "valtio";
import { Suspense, useEffect, useState } from "react";
import Error from "../app/error";


// Initialize default map state using proxy
const [state] = useMap([]);

const isLayerToggled = (layerName) => {
    let toggledNames = state.layers.toggled?.map(layer => layer.name);
    return toggledNames?.includes(layerName) ?? false;
};

const shouldDisableLayer = (layerName) => {
    let layerNames = state.layers.all.map(layer => layer.name);
    return !layerNames?.includes(layerName) ?? true;
}

const showLayer = (layerId) => {
    let layer = state.layers.all?.find(layer => layer.id == layerId);
    if (layer) {
        state.layers.toggled.push(layer);
    }
};

const hideLayer = (layerId) => {
    if (!layerId) return null;
    let layers = state.layers.toggled.filter(layer => layer.id !== layerId);
    state.layers.toggled = [...layers];
};

const handleLayerChecked = (e) => {
    let layerId = e.target.value;
    let checked = isLayerToggled(layerId);
    if (checked) {
        hideLayer(layerId);
    } else {
        showLayer(layerId);
    };
}

const clearToggableLayers = () => {
    state.layers.toggled = [];
};

const selectAllToggableLayers = () => {
    state.layers.toggled = [...state.layers.toggleable];
}

const setBasemap = (e) => state.basemap.setBasemap(e.target.value);


function MapWidget({ geographies }) {

    useEffect(() => {
        state.data.setGeographies(geographies);
    })

    // Take read-only snapshot for optimized rendering
    const snap = useSnapshot(state);

    return (
        <div className="grid grid-cols-12 m-0 p-0">
            <div className="relative w-3/4 overflow-hidden" style={{width: 1000, height: 1000}}>
                <DeckGL
                    layers={snap.layers.toggled}
                    initialViewState={snap.viewport.current}
                    controller={true}
                >
                    <Map
                        mapStyle={snap.basemap.selected.url}
                        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN}
                    />
                </DeckGL>
                <div className="absolute right-4 top-4 bg-white p-2">
                <Suspense>
                    <MapControlPanel
                        snap={snap}
                        isLayerToggled={isLayerToggled}
                        shouldDisableLayer={shouldDisableLayer}
                        selectAllToggableLayers={selectAllToggableLayers}
                        clearToggableLayers={clearToggableLayers}
                        handleLayerChecked={handleLayerChecked}
                        setBasemap={setBasemap}
                    />
                    </Suspense>
                </div>
            </div>
        </div>
    );
}

export default MapWidget;
