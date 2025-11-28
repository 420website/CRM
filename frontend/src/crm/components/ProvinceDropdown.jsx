export default function ProvinceDropdown({ value, handleChange }) {
  const provinceMap = [
    "Alberta",
    "British Columbia",
    "Manitoba",
    "Nova Scotia",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Northwest Territories",
    "Nunavut",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
    "Yukon",
  ];

  return (
    <div>
      <label
        htmlFor="province"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Province
      </label>
      <select
        id="province"
        name="province"
        value={value}
        onChange={handleChange}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
      >
        <option value="">Select</option>
        {/* Most Frequently Used */}
        {provinceMap.map((value, index) => (
          <option key={index} value={value}>
            {value}
          </option>
        ))}
      </select>
    </div>
  );
}
