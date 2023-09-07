/**
 * An autocomplete search bar.
 */

"use client";

import classNames from "classnames";
import { memo, useState, Suspense } from "react";
import { useGeoSearch } from "@/hooks/useGeoSearch";
import { useSnapshot } from "valtio";
import { debounce } from "@/lib/utils";
import Dropdown from "@/components/Dropdown";


const [state] = useGeoSearch("");

function Autocomplete({ onSelect }) {

    const [open, setOpen] = useState(false);
    const snap = useSnapshot(state);
    const handleClick = (geo) => {
        setOpen(false);
        state.query = geo.name;
        onSelect(geo.id);
    }

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
                    value={snap.query}
                    className="input input-bordered w-full pl-10"
                    onChange={(e) => debounce(state.setQuery(e.target.value), 50)}
                    placeholder="Type something..."
                    tabIndex={0}
                />
            </div>
            <Suspense>
                <Dropdown snap={snap} handleClick={handleClick}/>
            </Suspense>
        </div>
    );
}

export default memo(Autocomplete);
