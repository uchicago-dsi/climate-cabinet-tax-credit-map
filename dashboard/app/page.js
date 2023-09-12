"use client";
import { useState, useEffect, useLayoutEffect, useRef } from "react";
import { useSnapshot } from "valtio";

import { state, updateMapZoom } from "@/lib/state";

import Header from "../components/Header";
import SearchBar from "../components/SearchBar";
import Tooltip from "../components/Tooltip";
import DeckGLMap from "../components/DeckGLMap";
import ControlPanel from "../components/ControlPanel";
import SummaryStats from "../components/SummaryStats";
import Footer from "../components/Footer";
import { loadData } from "@/lib/data";

// TODO: This doesn't work?
import "../app/globals.css";

export default function Home() {
  const snapshot = useSnapshot(state);

  // load JSON and CSV data
  useEffect(() => {
    loadData();
  }, []);

  // Handling resizing of container to dynamically update map bounding box
  const containerRef = useRef(null);
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const width = containerRef.current.getBoundingClientRect().width;
        const height = containerRef.current.getBoundingClientRect().height;
        state.containerWidth = width;
        state.containerHeight = height;
      }
    };

    // TODO: this timeout is weird and I probably shouldn't have to actually do this
    setTimeout(handleResize, 200);
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  if (!snapshot.isDataLoaded) {
    return <div className="p-10">Loading...</div>;
  }

  return (
    <main className="w-screen">
      <div className="max-w-7xl mx-auto py-5">
        <Header />
      </div>
      <div className="max-w-7xl mx-auto">
        <SearchBar />
      </div>
      {/* add this in order to resize <div className="relative w-3/4" ref={containerRef}> */}
      <div className="max-w-7xl mx-auto flex py-10">
        <div className="relative w-3/4 overflow-hidden" ref={containerRef}>
          {/* <Tooltip /> */}
          <DeckGLMap />
          <div className="absolute right-4 top-4 bg-white p-2">
            <ControlPanel />
          </div>
        </div>
        <div className="flex flex-col w-1/4 h-[75vh] overflow-hidden px-5">
          <SummaryStats />
        </div>
      </div>
      <div className="w-full py-5">
        <Footer />
      </div>
    </main>
  );
}
