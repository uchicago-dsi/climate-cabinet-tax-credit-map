"use client";
// app.js
import React, { useState, useEffect } from "react";
import { proxy, useSnapshot } from "valtio";

// import { state } from "../lib/state";

import DeckGL from "@deck.gl/react";
import { LineLayer, IconLayer, GeoJsonLayer } from "@deck.gl/layers";
import { COORDINATE_SYSTEM } from "@deck.gl/core";

import { Map } from "react-map-gl";

// import colorbrewer from "colorbrewer";
// import tinycolor from "tinycolor2";
import { ScatterplotLayer } from "deck.gl";

// TODO: Is it ok load this client side? Seems like maybe it is for Mapbox?
const MAPBOX_ACCESS_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

export default function DeckGLMap() {
  const dummyViewState = {
    latitude: 37.7751,
    longitude: -122.4193,
    zoom: 11,
    bearing: 0,
    pitch: 0,
  };

  const deck = (
    <DeckGL
      initialViewState={dummyViewState}
      controller={true}
      //   layers={displayLayers}
      pickingRadius={50} //TODO: This behaves strangely and only works when zoomed out?
    >
      <Map
        mapStyle="mapbox://styles/mapbox/streets-v12"
        mapboxAccessToken={MAPBOX_ACCESS_TOKEN}
      />
    </DeckGL>
  );

  return deck;
}

{
  /* Legend code
  <div id="legend">
        {Object.entries(plantColorPalette).map(([key, color]) => (
          <div key={key} className="flex items-center">
            <div
              className="swatch"
              style={{
                background: `rgb(${color.slice(0, 3).join(",")},${
                  color[3] / 255
                })`,
              }}
            ></div>
            <div className="label">{key}</div>
          </div>
        ))} */
}
{
  /* </div> */
}
