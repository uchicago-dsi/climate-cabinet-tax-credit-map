/**
 * A custom "hook" for managing DeckGL GeoJSON map layers.
 */
import { useMemo } from "react";
import { layerConfig } from "@/config/layers";
import { MVTLayer } from '@deck.gl/geo-layers';
import { useSetTooltipStore } from "./useTooltipStore";

function useLayers(features, layerState) {

    /**
     * Initializes data for hover events.
     */
    const setHoverInfo = useSetTooltipStore();

    
    const mapName = (dataset) => {
        const geoType = dataset.properties.geography_type;
        const name = dataset.properties.name;
        if (geoType === "county") {
            return name.split(",")[0].toUpperCase();
        }
        else if (geoType === "distressed") {
            return `DISTRESSED ZIP CODE ${name}`
        }
        return name;
    }


    /**
     * Groups GeoJSON features by geography type to form datasets.
     */
    const geoDatasets = useMemo(() => features?.reduce((grp, geo) => {
            let key = geo.properties.geography_type;
            if (key === "state") return grp;
            grp[key] = grp[key] ?? [];
            grp[key].push(mapName(geo));
            return grp;
        }, {}),[features]);


    /**
     * A constant reference to all the GeoJSON layers currently holding data.
     */
    const _allLayers =  Object.entries(geoDatasets || {}).map(([key, dataset], _) => {
        let config = layerConfig.find(c => c.externalId === key);
        let active = layerState?.[config.id]?.visible || true;
        const getLayerColorOrEmpty = ( feature ) => {
            if (active && dataset.includes(feature.properties.name)) {
                return config.fillColor;
            }
            return [0,0,0,0]
        }
        const layer = new MVTLayer({
            id: config.id,
            data: `https://a.tiles.mapbox.com/v4/${config.mapboxTilesetId}/{z}/{x}/{y}.vector.pbf?access_token=${process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN}`,
            opacity: config.opacity,
            stroked: true,
            filled: true,
            extruded: false,
            wireframe: false,
            getFillColor: getLayerColorOrEmpty,
            updateTriggers: {
              getFillColor: [layerState]
            },
            getLineColor: [255, 255, 255],
            getLineWidth: 50,
            pickable: active,
            visible: active,
            onHover: (layer) => {
                // Parse properties from layer object
                let props = layer?.object?.properties;
                let geoType = props?.geoType;
                let name = props?.name;

                // If hovering over geography, update state
                if (geoType && dataset.includes(name)) {
                    setHoverInfo({
                        name: name,
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
