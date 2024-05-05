"use client";

/**
 * A dropdown item indicating that no matches/selections are available.
 */

function DropdownNullOption({ index, message }) {
  return (
    <li
      key={index}
      tabIndex={index + 1}
      className="border-b border-b-base-content/10 w-full text-lg"
    >
      {message}
    </li>
  );
}

export default DropdownNullOption;
