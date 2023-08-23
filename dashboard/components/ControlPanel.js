"use client";
import React, { useState, useEffect } from "react";
import { useSnapshot } from "valtio";

export default function ControlPanel() {
  const [expanded, setExpanded] = useState(true);
  const layers = ["Justice 40", "Low Income", "Energy", "Counties"];
  const mapView = ["Political Basemap", "Satellite Basemap"];

  return (
    <div className="w-full max-w-xs mx-auto">
      <p className="text-center">Select Layers</p>
      <div className="flex justify-center py-2">
        <button
          className="btn btn-sm normal-case"
          onClick={() => setExpanded((e) => !e)}
        >
          {expanded ? "Collapse Menu" : "Show Menu"}
        </button>
      </div>
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
              //checked={snapshot.filteredStates.includes(option)}
              //onChange={handleCheckboxChange}
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
            // onClick={selectAll}
          >
            All
          </button>
          <button
            className="btn join-item btn-sm normal-case"
            // onClick={selectNone}
          >
            None
          </button>
        </div>
        <div className="divider m-0"></div>
        {mapView.map((option, index) => (
          <label key={index} className="label flex cursor-pointer py-1">
            <input
              className="checkbox-sm"
              value={option}
              type="radio"
              name="mapLayer"
            ></input>
            <span className="label-text px-2">{option}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
