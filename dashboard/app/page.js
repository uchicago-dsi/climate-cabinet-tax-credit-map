"use client";
import { useState, useEffect } from "react";
import { useSnapshot } from "valtio";

import { state } from "@/lib/state";

import Header from "../components/Header";
import SearchBar from "../components/SearchBar";
import Tooltip from "../components/Tooltip";
import DeckGLMap from "../components/DeckGLMap";
import ControlPanel from "../components/ControlPanel";
import SummaryStats from "../components/SummaryStats";
import Footer from "../components/Footer";
import { loadData } from "@/lib/data";

export default function Home() {
  const snapshot = useSnapshot(state);

  // load JSON and CSV data
  useEffect(() => {
    loadData();
  }, []);

  if (!snapshot.isDataLoaded) {
    return <div>Loading...</div>;
  }

  console.log(state.stateNames);

  return (
    <main className="w-full">
      <div className="w-full p-5">
        <Header />
      </div>
      <div className="w-full p-5">
        <SearchBar />
      </div>
      {/* add this in order to resize <div className="relative w-3/4" ref={containerRef}> */}
      <div className="flex w-full px-20">
        <div className="relative w-3/4 overflow-hidden">
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
      <div className="p-5">
        <Footer />
      </div>
    </main>
  );
}
