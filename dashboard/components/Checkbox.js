/**
 * A checkbox.
 */


function Checkbox({ option, checked, disabled, onClick }) {  
  
  return (
        <label className="label flex cursor-pointer py-1">
            <input
              className="checkbox-sm"
              type="checkbox"
              value={option}
              checked={checked}
              disabled={disabled}
              onClick={onClick}
            />
            <span className="pl-5">
              {option}
            </span>
        </label>
    );
}

export default Checkbox;