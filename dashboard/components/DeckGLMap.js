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
  return (
    <div>
      <h4>Mappy</h4>
    </div>
  );
}
