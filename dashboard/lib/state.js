"use client";
import { proxy, useSnapshot } from "valtio";
import { useEffect } from "react";

import bbox from "@turf/bbox";
import { WebMercatorViewport } from "@deck.gl/core";

export const state = proxy({
  filteredLayers: [],
  selectedMap: "Political Basemap",
  states: [],
  stateNames: [],
  isDataLoaded: false,
  searchValue: "Alabama",
  searchGeometry: null, // TODO: does this need a default?

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

export function updateSearchGeo(searchValue) {
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
      padding: { top: 20, bottom: 20, left: 20, right: 20 },
    }
  );

  //   const boundingBox = bbox(currentGeojson);
  //   const fittedViewport = new WebMercatorViewport(
  //     state.containerWidth,
  //     state.containerHeight
  //   );

  //   const currentLatLonZoom = fittedViewport.fitBounds(
  //     [
  //       [boundingBox[0], boundingBox[1]],
  //       [boundingBox[2], boundingBox[3]],
  //     ],
  //     {
  //       width: state.containerWidth,
  //       height: state.containerHeight,
  //       padding: { top: 20, bottom: 20, left: 20, right: 20 },
  //     }
  //   );

  const mapZoom = {
    longitude: currentLatLonZoom.longitude,
    latitude: currentLatLonZoom.latitude,
    zoom: currentLatLonZoom.zoom,

    pitch: 0,
    bearing: 0,
  };

  // do it this way to avoid extensibility errors
  state.mapZoom = { ...mapZoom };
}
