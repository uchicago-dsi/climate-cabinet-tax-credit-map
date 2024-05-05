"use client";

/**
 * A radio button.
 */

function RadioButton({ option, name, isChecked, onChange }) {
  return (
    <label className="label flex cursor-pointer py-1">
      <input
        className="checkbox-sm"
        value={option}
        type="radio"
        name={name}
        checked={isChecked}
        onChange={onChange}
      />
      <span className="px-2">{name}</span>
    </label>
  );
}

export default RadioButton;
