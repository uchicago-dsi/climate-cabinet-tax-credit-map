"use client";

/**
 * A dropdown item.
 */

function DropdownOption({ index, onClick, item }) {
  return (
    <li
      key={index}
      tabIndex={index + 1}
      className="border-b border-b-base-content/10 w-full text-lg"
    >
      <button value={item} onClick={onClick}>
        {`${item.name.toUpperCase()} (${item.geography_type.toUpperCase()})`}
      </button>
    </li>
  );
}

export default DropdownOption;
