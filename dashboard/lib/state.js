"use client";
import { proxy, useSnapshot } from "valtio";
import { useEffect } from "react";

import bbox from "@turf/bbox";
import { WebMercatorViewport } from "@deck.gl/core";

export const state = proxy({
  layers: [],
  filteredLayers: [],
  selectedMap: "Political Basemap", // default to the political view
  states: [],
  stateNames: [],
  isDataLoaded: false,

  containerWidth: 0,
  containerHeight: 0,
  mapZoom: {
    longitude: -119.272009,
    latitude: 37.421476393980676,
    zoom: 5.386212475852944,
    pitch: 0,
    bearing: 0,
  },
});

export function updateFilteredData() {
  console.log(state.filteredLayers);
  // choose the filtered areas to display
  // TODO: row properties isn't going to be selected based upon state
  //   state.filteredLayers = state.layers.features.filter((row) => {
  //     if (state.filteredStates.includes(row.properties.state)) {
  //       return true;
  //     } else {
  //       return false;
  //     }
  //   });
}

export function updateSearchGeo() {
  const foundFeature = state.states.features.find(
    (feature) => feature.properties.NAME === state.searchValue
  );

  if (foundFeature) {
    state.searchGeometry = foundFeature.geometry;
  } else {
    state.searchGeometry = null;
  }
  updateMapZoom();
}

export function updateMapZoom() {
  // TODO: this default setting doesn't work
  var zoomGeoJSON = state.searchGeometry
    ? state.searchGeometry
    : state.states.features[0].geometry;

  const currentGeojson = {
    type: "Feature",
    geometry: zoomGeoJSON,
  };

  const boundingBox = bbox(currentGeojson);
  const fittedViewport = new WebMercatorViewport(
    state.containerWidth,
    state.containerHeight
  );

  const currentLatLonZoom = fittedViewport.fitBounds(
    [
      [boundingBox[0], boundingBox[1]],
      [boundingBox[2], boundingBox[3]],
    ],
    {
      width: state.containerWidth,
      height: state.containerHeight,
      // TODO: padding isn't working
      padding: { top: 30, bottom: 30, left: 30, right: 30 },
    }
  );

  const mapZoom = {
    longitude: currentLatLonZoom.longitude,
    latitude: currentLatLonZoom.latitude,
    zoom: currentLatLonZoom.zoom,

    pitch: 0,
    bearing: 0,
  };

  // unpack to avoid extensibility errors
  state.mapZoom = { ...mapZoom };
}
