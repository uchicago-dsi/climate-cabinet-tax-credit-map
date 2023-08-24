"use client";
import React, { useEffect, useState } from "react";
import { snapshot, useSnapshot } from "valtio";
import { state } from "@/lib/state";

import Autocomplete from "./Autocomplete";

export default function AutocompleteLogic() {
  const snapshot = useSnapshot(state);

  // query typed by user
  const [val, setVal] = useState("");

  // a list to hold all the countries
  //   const [options, setOptions] = useState([]);

  console.log();

  // a list to show on the dropdown when user types
  const [items, setItems] = useState([]);

  //   setOptions(state.stateNames);

  // query rest countries api and set the countries list
  //   useEffect(() => {
  //     async function fetchData() {
  //       const url = "https://restcountries.com/v3.1/all?fields=name";
  //       const response = await fetch(url);
  //       const countries = await response.json();
  //       const newItems = countries.map((p) => p.name.common).sort();
  //       setCountries(newItems);
  //     }

  //     fetchData();
  //   }, []);

  useEffect(() => {
    setItems(snapshot.stateNames);
  }, []);

  useEffect(() => {
    // if there is no value, return the countries list.
    if (!val) {
      setItems(snapshot.stateNames);
      return;
    }

    // if the val changes, we filter items so that it can be filtered. and set it as new state
    const newItems = snapshot.stateNames
      .filter((p) => p.toLowerCase().includes(val.toLowerCase()))
      .sort();
    setItems(newItems);
  }, [snapshot.stateNames, val]);

  // use the common auto complete component here.
  return <Autocomplete items={items} value={val} onChange={setVal} />;
}
