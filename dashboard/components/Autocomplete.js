"use client";
import { memo, useRef, useState } from "react";
import classNames from "classnames";

function Autocomplete(props) {
  const { items, value, onChange } = props;
  const ref = useRef(null);
  // TODO: standard question about local vs global state
  const [open, setOpen] = useState(false);

  return (
    <div
      className={classNames({
        "dropdown w-full": true,
        "dropdown-open": open,
      })}
      ref={ref}
    >
      <input
        type="text"
        className="input input-bordered w-full"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Type something.."
        tabIndex={0}
      />
      {value && (
        <div className="dropdown-content bg-base-200 top-14 max-h-96 overflow-auto flex-col rounded-md">
          <ul
            className="menu menu-compact"
            style={{ width: ref.current?.clientWidth }}
          >
            {items.map((item, index) => {
              return (
                <li
                  key={index}
                  tabIndex={index + 1}
                  onClick={() => {
                    onChange(item);
                    setOpen(false);
                  }}
                  className="border-b border-b-base-content/10 w-full"
                >
                  <button>{item}</button>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

export default memo(Autocomplete);
