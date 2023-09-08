"use client";
import "@fortawesome/fontawesome-free/css/all.min.css";
import { memo, useState } from "react";
// import Autocomplete from "./Autocomplete";
import AutocompleteLogic from "./AutocompleteLogic";

export default function SearchBar() {
  return (
    <div className="flex flex-col items-center">
      <div
        className="w-screen px-8 py-10 bg-center bg-cover bg-no-repeat"
        style={{ backgroundImage: `url('/images/c3titlebanner2.jpg')` }}
      >
        <div className="container mx-auto">
          <h1 className="humani-title">Map Search Tool</h1>
        </div>
      </div>
      <div className="w-3/4">
        <p className="px-20 py-5">
          Enter the name of a state, county, municipality or rural electric
          cooperative to view its Justice 40 communities, energy communities,
          and designated low-income census tracts and MSAs on an interactive
          map. The map will also show a description of available tax credit
          programs
        </p>
      </div>
      <div className="relative m-2 z-50">
        <AutocompleteLogic />
      </div>
    </div>
  );
}
