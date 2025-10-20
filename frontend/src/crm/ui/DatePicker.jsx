import { X } from "lucide-react";

const DatePicker = ({
  name,
  value,
  onChange,
  className,
  style,
  placeholder = "Select date",
}) => {
  const formatDate = (dateString) => {
    if (!dateString) return "";
    const dateParts = dateString.split("-");
    const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const handleClear = (e) => {
    e.stopPropagation();
    e.preventDefault();
    onChange({ target: { name, value: "" } });
  };

  const handleDisplayClick = () => {
    const picker = document.getElementById(`${name}Picker`);
    if (picker.showPicker) {
      try {
        picker.showPicker();
      } catch (error) {
        picker.click();
      }
    } else {
      picker.click();
    }
  };

  const pickerId = `${name}Picker`;
  const css = className ? `${className} pr-8` : "pr-8";

  return (
    <div className="relative">
      <input
        type="text"
        id={name}
        name={name}
        value={formatDate(value)}
        readOnly
        onClick={handleDisplayClick}
        className={css}
        style={style}
        placeholder={placeholder}
      />
      {value && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-gray-400 hover:bg-gray-600 text-white flex items-center justify-center z-10 transition-colors"
        >
          <X size={12} strokeWidth={3} />
        </button>
      )}
      <input
        type="date"
        id={pickerId}
        value={value}
        onChange={onChange}
        name={name}
        className="absolute inset-0 opacity-0 cursor-pointer [&::-webkit-clear-button]:hidden [&::-webkit-inner-spin-button]:hidden [&::-webkit-calendar-picker-indicator]:opacity-100 [&::-webkit-calendar-picker-indicator]:absolute [&::-webkit-calendar-picker-indicator]:inset-0 [&::-webkit-calendar-picker-indicator]:w-full [&::-webkit-calendar-picker-indicator]:h-full [&::-webkit-calendar-picker-indicator]:cursor-pointer"
        style={style}
      />
    </div>
  );
};

export default DatePicker;
