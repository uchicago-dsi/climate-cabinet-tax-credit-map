"use client";
import "@fortawesome/fontawesome-free/css/all.min.css";
import { memo, useState } from "react";
// import Autocomplete from "./Autocomplete";
import AutocompleteLogic from "./AutocompleteLogic";

export default function SearchBar() {
  const [value, setValue] = useState("");
  const states = ["Illinois", "California"];

  return (
    <div className="flex flex-col items-center">
      <div className="text-center w-1/3">
        <h2>Map Search Tool</h2>
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
