"use client";
import React, { useState, useEffect } from "react";
import { useSnapshot } from "valtio";
import { state } from "../lib/state";

export default function ControlPanel() {
  // TODO: should I use both "state" and the react "state"
  const snapshot = useSnapshot(state);
  const [expanded, setExpanded] = useState(true);
  // TODO: default selection is not working
  const [selectedMap, setMapView] = useState("Political Basemap");

  // TODO: is there a difference between low income and distressed? Probably
  const layers = [
    "Justice 40",
    "Low Income",
    "Distressed",
    "Energy",
    "Counties",
  ];
  const mapViews = ["Political Basemap", "Satellite Basemap"];

  const selectAll = () => {
    state.filteredLayers = [...layers];
    // updateFilteredData();
  };

  const selectNone = () => {
    state.filteredLayers.length = 0;
    // updateFilteredData();
  };

  const handleCheckboxChange = (event) => {
    const { checked, value } = event.target;

    // adjust filtered states
    if (checked) {
      state.filteredLayers.push(value);
    } else {
      const index = state.filteredLayers.indexOf(value);
      if (index !== -1) {
        state.filteredLayers.splice(index, 1);
      }
    }

    // updateFilteredData();
  };

  const handleMapChange = (event) => {
    setMapView(event.target.value);
  };

  return (
    <div className="w-full max-w-xs mx-auto">
      <p className="text-center">Select Layers</p>
      <div
        className={`form-control h-0 overflow-hidden ${
          expanded && "h-auto overflow-auto max-h-full"
        }`}
      >
        <div className="divider m-0"></div>
        {layers.map((option, index) => (
          <label key={index} className="label flex cursor-pointer py-1">
            <input
              className="checkbox-sm"
              value={option}
              type="checkbox"
              checked={snapshot.filteredLayers.includes(option)}
              onChange={handleCheckboxChange}
            />
            <span
              // TODO: wtf why won't this text left align
              className="label-text"
            >
              {option}
            </span>
          </label>
        ))}
        <div className="join justify-center py-2">
          <button
            className="btn join-item btn-sm normal-case"
            onClick={selectAll}
          >
            All
          </button>
          <button
            className="btn join-item btn-sm normal-case"
            onClick={selectNone}
          >
            None
          </button>
        </div>
        <div className="divider m-0"></div>
        {mapViews.map((option, index) => (
          <label key={index} className="label flex cursor-pointer py-1">
            <input
              className="checkbox-sm"
              value={option}
              type="radio"
              name="mapLayer"
              checked={selectedMap === option}
              onChange={handleMapChange}
            ></input>
            <span className="label-text px-2">{option}</span>
          </label>
        ))}
      </div>
      <div className="flex justify-center py-2">
        <button
          className="btn btn-sm normal-case"
          onClick={() => setExpanded((e) => !e)}
        >
          {expanded ? "Collapse Menu" : "Show Menu"}
        </button>
      </div>
    </div>
  );
}
