/**
 * A dropdown item indicating that no matches/selections are available.
 */

"use client"

function DropdownNullOption({ index, message }) {
    return (
        <li
          key={index}
          tabIndex={index + 1}
          className="border-b border-b-base-content/10 w-full"
        >
          {message}
        </li>
    );
}

export default DropdownNullOption;