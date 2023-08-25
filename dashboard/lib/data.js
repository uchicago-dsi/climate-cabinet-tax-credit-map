"use client";
import { state, updateFilteredData } from "../lib/state";
import { updateMapZoom } from "../lib/state";

const STATES_GEOJSON = "../data/state_boundaries.geojson";

const getJSON = async (dataPath) => {
  const response = await fetch(dataPath);
  return await response.json();
};

export const loadData = async () => {
  // Read raw files
  state.states = await getJSON(STATES_GEOJSON);

  // Get list of states
  state.stateNames = state.states.features
    .map((feature) => feature.properties.NAME)
    .filter((value, index, array) => array.indexOf(value) === index)
    .sort();

  state.isDataLoaded = true;
};
