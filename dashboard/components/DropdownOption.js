/**
 * A dropdown item.
 */

"use client"

function DropdownOption({ index, onClick, item }) {
    return (
        <li
          key={index}
          tabIndex={index + 1}
          className="border-b border-b-base-content/10 w-full"
        >
          <button value={item} onClick={onClick}>
            {item.name}
          </button>
        </li>
    );
}

export default DropdownOption;