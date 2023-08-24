"use client";
import React, { useEffect, useState } from "react";
import { snapshot, useSnapshot } from "valtio";
import { state } from "@/lib/state";

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

  // use the common auto complete component here.
  return <Autocomplete items={items} value={query} onChange={setQuery} />;
}
