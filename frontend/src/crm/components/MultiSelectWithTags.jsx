import { useState, useRef, useEffect } from "react";

export default function MultiSelectWithTags({
  options,
  values,
  handleRemove,
  handleAdd,
  placeholder = "Select...",
  header = "Selction Menu",
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const wrapperRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Filter options based on search term and exclude already selected
  const filteredOptions = options.filter(
    (opt) =>
      opt.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !values.includes(opt),
  );

  return (
    <div ref={wrapperRef} className="relative w-full">
      <label
        htmlFor="MultiSelectionHeader"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        {header}
      </label>
      {/* Tags display */}
      <div className="flex flex-wrap gap-2 mb-2">
        {values.map((item, index) => (
          <span
            key={item}
            className="text-xs border border-black text-black px-3 py-1 rounded-full flex items-center gap-2"
          >
            {item}
            <button
              type="button"
              onClick={() => handleRemove(item)}
              className="hover:text-blue-600 font-bold"
            >
              ×
            </button>
          </span>
        ))}
      </div>

      {/* Search input */}
      <div ref={wrapperRef}>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={values.length === 0 ? placeholder : "Add more..."}
          className="w-full border border-gray-300 rounded px-3 py-2"
        />

        {/* Dropdown */}
        {isOpen && filteredOptions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-60 overflow-y-auto">
            {filteredOptions.map((option) => (
              <div
                key={option}
                onClick={() => handleAdd(option)}
                className="px-3 py-2 hover:bg-blue-50 cursor-pointer"
              >
                {option}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
