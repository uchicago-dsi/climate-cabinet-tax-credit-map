/**
 * A custom "hook" for managing DeckGL GeoJSON map layers.
 */
import { useMemo } from "react";
import { layerConfig } from "@/config/layers";
import { GeoJsonLayer } from "@deck.gl/layers";
import { useSetTooltipStore } from "./useTooltipStore";

function useLayers(features, layerState) {

    /**
     * Initializes data for hover events.
     */
    const setHoverInfo = useSetTooltipStore();

    const geoDatasets = useMemo(() => features?.reduce((grp, geo) => {
            let key = geo.properties.geography_type;
            if (key === "state") return grp;
            grp[key] = grp[key] ?? [];
            grp[key].push(geo);
            return grp;
        }, {}),[features]);

    /**
     * A constant reference to all the GeoJSON layers currently holding data.
     */
    const _allLayers =  Object.entries(geoDatasets || {}).map(([key, dataset], _) => {
        let config = layerConfig.find(c => c.externalId === key);
        let active = layerState?.[config.id]?.visible || true;
        const layer = new GeoJsonLayer({
            id: config.id,
            data: dataset,
            opacity: config.opacity,
            stroked: true,
            filled: true,
            extruded: false,
            wireframe: true,
            getFillColor: config.fillColor,
            getLineColor: [255, 255, 255],
            getLineWidth: 300,
            pickable: active,
            visible: active,
            onHover: (layer) => {
                // Parse properties from layer object
                let props = layer?.object?.properties;
                let geoType = props?.geography_type;
                let geoName = `${config.id}: ${props?.name}`;
                // // If still hovering over same geography, don't update state
                // If hovering over new geography, update state
                if (geoType) {
                    setHoverInfo({
                        name: geoName,
                        x: layer?.x,
                        y: layer?.y
                    });
                    return;
                }
                
                // Otherwise, if not hovering over a geography, reset state
                setHoverInfo(null); 
            }
        })
        layerState[config.id].hasData = true;
        return layer
    });

    /**
     * A snapshot of the current layer state. Used for GET requests.
     */
    const getLayer = (layerId) => {
        return _allLayers.find(layer => layer.id === layerId) ?? null;
    }

    /**
     * Returns all the GeoJSON layers currently holding data.
     * 
     * @returns The layers.
     */
    const getAllLayers = () => _allLayers;

    /**
     * Returns the ids of the layers that generally can be toggled,
     * regardless of whether data currently exists for that layer or not.
     * Used upstream for populating the layer display options on the
     * map control panel.
     * 
     * @returns The ids.
     */
    const getToggleOptions = () => layerConfig.reduce((arr, layer) => {
        if (layer.canToggle) arr.push(layer.id);
        return arr;
    }, []);

    /**
     * Returns a boolean indicating whether any data exists for the given layer.
     * For example, a user search query might not have resulted in a Justice 40
     * community being returned from the API. Used upstream for disabling
     * layer display options on the map control panel.
     * 
     * @param {*} layerId The unique identifier for the layer.
     * @returns The `true` or `false` value.
     */
    const layerHasData = (layerId) => {
        let layer = _allLayers.find(layer => layer.id === layerId) ?? null;
        return layer !== null;
    };

    /**
     * Returns a boolean indicating whether the layer is currently displayed.
     * 
     * @param {*} layerId The unique identifier for the layer.
     * @returns The `true` or `false` value.
     */
    const layerIsVisible = (layerId) => {
        return layerState[layerId].visible;
    };

    /**
     * Returns the layers currently visible on the map.
     * 
     * @returns The visible/displayed layers.
     */
    const getVisibleLayers = () => {
        return _allLayers.filter(layer => layerIsVisible(layer.id));
    }

    /**
     * Changes the visibility of all toggleable layers to `true`.     * 
     */
    const showAllLayers = () => {
        Object.keys(layerState).forEach(id => {
            layerState[id].visible = true;
            layerState[id].pickable = true;
        });
    };

    /**
     * Changes the visiblity of all toggleable layers to `false`.
     */
    const hideAllLayers = () => {
        let toggleable = getToggleOptions();
        Object.keys(layerState).forEach(id => {
            if (toggleable.includes(id)) {
                layerState[id].visible = false;
                layerState[id].pickable = false;
            }
        });
    };

    /**
     * Flips the visiblity of the given layer.
     * 
     * @param {*} e The triggering event.
     */
    const toggleLayer = (e) => {
        if (e) {
            let layerId = e.target.value;
            layerState[layerId].visible = !layerState?.[layerId].visible;
        }
    };

    return {
        // hoverInfo,
        getLayer,
        getAllLayers,
        getVisibleLayers,
        getToggleOptions,
        layerHasData,
        layerIsVisible,
        showAllLayers,
        hideAllLayers,
        toggleLayer
    };
}


export { useLayers }
