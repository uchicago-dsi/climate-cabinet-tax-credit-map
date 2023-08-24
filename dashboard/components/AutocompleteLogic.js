"use client";

import React, { useEffect, useState } from "react";
import Autocomplete from "./Autocomplete";

export default function AutocompleteLogic() {
  // query typed by user
  const [val, setVal] = useState("");

  // a list to hold all the countries
  const [countries, setCountries] = useState([]);

  // a list to show on the dropdown when user types
  const [items, setItems] = useState([]);

  // query rest countries api and set the countries list
  useEffect(() => {
    async function fetchData() {
      const url = "https://restcountries.com/v3.1/all?fields=name";
      const response = await fetch(url);
      const countries = await response.json();
      const newItems = countries.map((p) => p.name.common).sort();
      setCountries(newItems);
    }

    fetchData();
  }, []);

  useEffect(() => {
    // if there is no value, return the countries list.
    if (!val) {
      setItems(countries);
      return;
    }

    // if the val changes, we filter items so that it can be filtered. and set it as new state
    const newItems = countries
      .filter((p) => p.toLowerCase().includes(val.toLowerCase()))
      .sort();
    setItems(newItems);
  }, [countries, val]);

  // use the common auto complete component here.
  return <Autocomplete items={items} value={val} onChange={setVal} />;
}
