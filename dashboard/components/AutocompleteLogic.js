"use client";
import React, { useEffect, useState } from "react";
import { snapshot, useSnapshot } from "valtio";
import { state, updateSearchGeo } from "@/lib/state";

import Autocomplete from "./Autocomplete";

export default function AutocompleteLogic() {
  const snapshot = useSnapshot(state);

  // query typed by user
  const [query, setQuery] = useState("");

  // a list to show on the dropdown when user types
  const [items, setItems] = useState([]);

  useEffect(() => {
    setItems(snapshot.stateNames);
  }, []);

  useEffect(() => {
    // if there is no value, return full list
    if (!query) {
      setItems(snapshot.stateNames);
      return;
    }

    // get the choices that match user input so far
    const newItems = snapshot.stateNames
      .filter((p) => p.toLowerCase().includes(query.toLowerCase()))
      .sort();
    setItems(newItems);
  }, [snapshot.stateNames, query]);

  function handleSubmission() {
    if (items.length > 0) {
      const firstItem = items[0];
      state.searchValue = firstItem;
      updateSearchGeo(snapshot.searchValue);
    }
  }

  // The Autocomplete component includes the input
  return (
    <div className="flex flex-row">
      <Autocomplete items={items} value={query} onChange={setQuery} />
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
        onClick={handleSubmission}
      >
        Submit
      </button>
    </div>
  );
}
