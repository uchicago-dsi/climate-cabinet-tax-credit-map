/**
 * A dropdown item.
 */

"use client";

function DropdownOption({ index, onClick, item }) {
  console.log(item);
  return (
    <li
      key={index}
      tabIndex={index + 1}
      className="border-b border-b-base-content/10 w-full text-lg"
    >
      <button value={item} onClick={onClick}>
        {item.name.toUpperCase()}
        {/* `${item.name.toUpperCase()} (${item.type.toUpperCase()})` */}
      </button>
    </li>
  );
}

export default DropdownOption;
