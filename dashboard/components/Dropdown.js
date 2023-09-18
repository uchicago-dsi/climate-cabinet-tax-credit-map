/**
 * A dropdown container for autocomplete search results.
 */

"use client";

import DropdownNullOption from "@/components/DropdownNullOption";
import DropdownOption from "@/components/DropdownOption";


function Dropdown({ snap, handleClick, nullMessage}) {

    let results = snap.results?.data;

    return (
        <div className="dropdown-content bg-base-200 top-14 max-h-96 overflow-auto flex-col rounded-md">
            <ul className="menu menu-compact">                    
            {
                results?.length > 0 ? results.map((value, idx) => {
                        return <DropdownOption
                                key={idx}
                                index={idx}
                                onClick={() => handleClick(value)} 
                                item={value} />
                        }) 
                    : <DropdownNullOption 
                        index={0} 
                        message={nullMessage} />
                }
            </ul>
        </div>
    );
}

export default Dropdown;