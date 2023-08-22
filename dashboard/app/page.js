"use client";
import Image from "next/image";

import Header from "../components/Header";
import SearchBar from "../components/SearchBar";
import Tooltip from "../components/Tooltip";
import DeckGLMap from "../components/DeckGLMap";
import ControlPanel from "../components/ControlPanel";
import SummaryStats from "../components/SummaryStats";
import Footer from "../components/Footer";

export default function Home() {
  return (
    <main className="w-full h-[100vh]">
      <div className="w-full">
        <Header />
      </div>
      <div>
        <SearchBar />
      </div>
      {/* add this in order to resize <div className="relative w-3/4" ref={containerRef}> */}
      <div className="flex w-full p-20">
        <div className="relative w-3/4">
          {/* <Tooltip /> */}
          <DeckGLMap />
          <div className="absolute right-4 top-4 bg-white p-2">
            <ControlPanel />
          </div>
        </div>
        <div className="flex flex-col w-1/4 h-[100vh] overflow-hidden">
          <SummaryStats />
        </div>
      </div>
      <div>
        <Footer />
      </div>
    </main>
  );
}
