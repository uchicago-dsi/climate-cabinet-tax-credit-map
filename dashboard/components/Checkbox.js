/**
 * A checkbox.
 */

function Checkbox({ option, checked, disabled, onChange }) {
  return (
    <label className="label flex cursor-pointer py-1">
      <input
        className="checkbox-sm"
        type="checkbox"
        value={option}
        checked={checked}
        disabled={disabled}
        onChange={onChange}
      />
      <span className="pl-5">{option}</span>
    </label>
  );
}

export default Checkbox;
