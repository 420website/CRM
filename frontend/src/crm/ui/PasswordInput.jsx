import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export default function PasswordInput({
  formData,
  handleInputChange,
  required,
}) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div id="password" className="mb-4 scroll-mt-[60px]">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Password <span className="text-red-500">*</span>
      </label>
      <div className="relative w-full md:w-1/2">
        <input
          type={showPassword ? "text" : "password"}
          name="password"
          value={formData.password}
          onChange={handleInputChange}
          // required={required}
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black pr-10"
          style={{ height: "40px" }}
        />
        <button
          type="button"
          onClick={() => setShowPassword((prev) => !prev)}
          onMouseDown={(e) => e.preventDefault()}
          className="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700 focus:outline-none z-10"
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </div>
  );
}
