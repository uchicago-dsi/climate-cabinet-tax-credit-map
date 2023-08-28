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
      <div>
        <h2>Map Search Tool</h2>
      </div>
      <div className="relative m-2 z-50">
        <AutocompleteLogic />
      </div>
    </div>
  );
}
