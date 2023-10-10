/**
 * An autocomplete search bar.
 */

"use client";

import Dropdown from "@/components/Dropdown";
import classNames from "classnames";
import debounce from "lodash/debounce";
import { memo, useCallback, useState, Suspense } from "react";
import { useSnapshot } from "valtio";
import { searchStore, reportStore } from "@/states/search";

function Autocomplete() {
  // Initialize value for search box
  const [innerValue, setInnerValue] = useState("");

  // Initialize visiblity of search results dropdown
  const [open, setOpen] = useState(false);

  // Define function to collapse search results and update selection on click
  const handleClick = (geo) => {
    setOpen(false);
    setInnerValue(geo.name);
    searchStore.setQuery(geo.name);
    searchStore.setSelected(geo);
  };

  // Define function to debounce user search queries
  const handleSearch = useCallback(
    debounce((value) => {
      searchStore.setQuery(value);
    }, 100),
    []
  );

  // Define function to handle new user search queries
  const handleTextInput = (e) => {
    setInnerValue(e.target.value);
    handleSearch(e.target.value);
  };

  // Take snapshot of state for rendering
  const snap = useSnapshot(searchStore);

  return (
    <div
      className={classNames({
        "dropdown w-full": true,
        "dropdown-open": open,
      })}
    >
      <div>
        <span className="absolute inset-y-0 left-0 flex items-center pl-2">
          <button className="p-1 focus:outline-none focus:shadow-outline bg-white border-white">
            <svg
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              className="w-6 h-6"
            >
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </span>
        <input
          type="search"
          value={innerValue}
          className="input input-bordered w-full pl-10"
          onChange={handleTextInput}
          placeholder="Type something..."
          tabIndex={0}
        />
      </div>
      <Suspense>
        <Dropdown
          snap={snap}
          handleClick={handleClick}
          nullMessage={"No results found."}
        />
      </Suspense>
    </div>
  );
}

export default memo(Autocomplete);
