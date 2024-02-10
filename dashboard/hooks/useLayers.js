/**
 * A custom "hook" for managing DeckGL GeoJSON map layers.
 */
import { useMemo } from "react";
import { layerConfig } from "@/config/layers";
import { MVTLayer } from "@deck.gl/geo-layers";
import { useSetTooltipStore } from "./useTooltipStore";

function useLayers(features, layerState) {
  /**
   * Initializes data for hover events.
   */
  const setHoverInfo = useSetTooltipStore();

  /**
   * Resets data state whenever new geographies are requested.
   */
  useMemo(() => {
    Object.keys(layerState).forEach((id) => {
      layerState[id].hasData = false;
    });
  }, [features]);

  /**
   * Groups GeoJSON features by geography type to form datasets.
   */
  const geoDatasets = useMemo(
    () =>
      features?.reduce(
        (grp, geo) => {
          let key = geo.properties.geography_type;
          if (key === "state") return grp;
          grp[key] = grp[key] ?? [];
          grp[key].push(geo.properties.name);
          return grp;
        },
        { county: [] }
      ),
    [features]
  );

  /**
   * A constant reference to all the GeoJSON layers currently holding data.
   */
  const _allLayers = Object.entries(geoDatasets || {}).map(
    ([key, dataset], _) => {
      let config = layerConfig.find((c) => c.externalId === key);
      let active = layerState?.[config.id]?.visible || true;
      const getLayerColorOrEmpty = (feature) => {
        if (active && dataset.includes(feature.properties.name)) {
          return config.fillColor;
        }
        return [0, 0, 0, 0];
      };
      const getWhiteOrEmpty = (feature) => {
        if (active && dataset.includes(feature.properties.name)) {
          return [255, 255, 255];
        }
        return key === "county" ? config.fillColor : [0, 0, 0, 0];
      };
      const layer = new MVTLayer({
        id: config.id,
        data: `https://a.tiles.mapbox.com/v4/${process.env.NEXT_PUBLIC_MAPBOX_USERNAME}.${config.mapboxTilesetName}/{z}/{x}/{y}.vector.pbf?access_token=${process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN}`,
        opacity: config.opacity,
        stroked: true,
        filled: true,
        extruded: false,
        wireframe: false,
        getFillColor: getLayerColorOrEmpty,
        updateTriggers: {
          getFillColor: [layerState],
        },
        getLineColor: getWhiteOrEmpty,
        getLineWidth: key === "county" ? 200 : 50,
        getLineDashArray: key === "county" ? [6, 4] : [0, 0],
        lineDashJustified: true,
        pickable: active,
        visible: active,
        onHover: (layer) => {
          // Parse properties from layer object
          let props = layer?.object?.properties;
          let geoType = props?.geography_type;
          let name = props?.name;

          // If hovering over geography, update state
          if (geoType && (geoType === "county" || dataset.includes(name))) {
            setHoverInfo({
              name: name,
              x: layer?.x,
              y: layer?.y,
            });
            return;
          }

          // Otherwise, if not hovering over a geography, reset state
          setHoverInfo(null);
        },
      });
      layerState[config.id].hasData = true;
      return layer;
    }
  );

  /**
   * A snapshot of the current layer state. Used for GET requests.
   */
  const getLayer = (layerId) => {
    return _allLayers.find((layer) => layer.id === layerId) ?? null;
  };

  /**
   * Returns the ids of the layers that generally can be toggled,
   * regardless of whether data currently exists for that layer or not.
   * Used upstream for populating the layer display options on the
   * map control panel.
   *
   * @returns The ids.
   */
  const getToggleOptions = () =>
    layerConfig.reduce((arr, layer) => {
      if (layer.canToggle) arr.push(layer.id);
      return arr;
    }, []);

  /**
   * Changes the visibility of all toggleable layers to `true`.     *
   */
  const showAllLayers = () => {
    Object.keys(layerState).forEach((id) => {
      layerState[id].visible = true;
    });
  };

  /**
   * Changes the visiblity of all toggleable layers to `false`.
   */
  const hideAllLayers = () => {
    let toggleable = getToggleOptions();
    Object.keys(layerState).forEach((id) => {
      if (toggleable.includes(id)) {
        layerState[id].visible = false;
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
    getToggleOptions,
    showAllLayers,
    hideAllLayers,
    toggleLayer,
  };
}

export { useLayers };
