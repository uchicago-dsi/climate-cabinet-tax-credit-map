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
        <div>
          <div>{item.name.toUpperCase()}</div>
          <div
            style={{
              fontSize: "smaller",
              color: "grey",
              marginTop: "4px",
            }}
          >
            {item.geography_type.toUpperCase()}
          </div>
        </div>
      </button>
    </li>
  );
}

export default DropdownOption;
