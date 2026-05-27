import { PROVINCES } from "../../constants";
import { useAuth } from "../../context/AuthContext";

export default function ProvinceDropdown({
  value,
  handleChange,
  required = false,
  all_provinces = true,
  formatting = "",
  fixedHeight = false,
}) {
  const { userLocationPermissions } = useAuth();
  let provinces = PROVINCES;

  if (!all_provinces && !userLocationPermissions.includes("All")) {
    provinces = userLocationPermissions;
  }

  const heightStyle = fixedHeight
    ? {
        height: "40px",
        minHeight: "40px",
        maxHeight: "40px",
      }
    : {};

  return (
    <div id="province" className="scroll-mt-[60px]">
      <label
        htmlFor="province"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Province {required && <span className="text-red-500">*</span>}
      </label>
      <select
        id="province"
        name="province"
        value={value}
        onChange={handleChange}
        className={`w-full px-3 py-2 border border-gray-300 rounded-md  focus:outline-none focus:ring-2 focus:ring-black ${formatting}`}
        style={heightStyle}
      >
        <option value="">Select</option>
        {/* Most Frequently Used */}
        {provinces.map((value, index) => (
          <option key={index} value={value}>
            {value}
          </option>
        ))}
      </select>
    </div>
  );
}
