import { useState } from "react";
import EmailTwoFactorVerify from "../components/EmailTwoFactorVerify";
import { AuthServices } from "../../services/authService";
import { tokenManager } from "../../tokenManager";
import { useAuth } from "../../context/AuthContext";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";

function InsertPin({ handleSubmit, formData, handleChange, error, loading }) {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="lg:h-[calc(100vh-400px)] bg-gray-50 flex flex-col justify-center m-4">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow rounded-lg sm:px-10">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Admin Access
          </h2>
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <label
                htmlFor="email"
                className="px-1 block text-sm font-medium text-gray-700 text-left"
              >
                Email
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black resize-y appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10  text-left  tracking-widest text-sm"
                  placeholder="Enter your email"
                />
              </div>
            </div>
            <div>
              <label
                htmlFor="password"
                className="px-1 block text-sm font-medium text-gray-700 text-left"
              >
                Password
              </label>
              <div className="mt-1 relative">
                {" "}
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black resize-y appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10  text-left  tracking-widest text-sm pr-10"
                  placeholder="Enter your password"
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
            <div>
              {/* Conditionally render the verification hint */}
              {error === "Please verify your email first" && (
                <p className="text-sm text-gray-700">
                  If you did not receive a verification email, please check your
                  spam folder or{" "}
                  <Link
                    to="/verify-email"
                    className="text-blue-600 hover:underline font-medium"
                  >
                    resend it here
                  </Link>
                  .
                </p>
              )}
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black disabled:bg-gray-300"
              >
                {loading ? "Verifying..." : "Continue"}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <button
              onClick={() => navigate("/")}
              className="w-full text-center text-sm text-gray-600 hover:text-gray-800"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const AdminPIN = () => {
  const location = useLocation();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showTwoFactor, setShowTwoFactor] = useState(false);
  const { setIsLoggedIn, setIsAuthenticatorMfaSetup, isAuthenticated } =
    useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const result = await AuthServices.login(formData.email, formData.password);

    if (result.success) {
      tokenManager.setAccessToken(result.data?.access_token);
      setIsLoggedIn(true);
      setIsAuthenticatorMfaSetup(result.data?.authenticator_mfa_setup);
      setShowTwoFactor(true);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }
    setLoading(false);
  };

  const onCancel = () => {
    setShowTwoFactor(false);
  };

  if (isAuthenticated) {
    return <Navigate to="/admin-menu" state={{ from: location }} replace />;
  }

  if (showTwoFactor) {
    return <EmailTwoFactorVerify email={formData.email} onCancel={onCancel} />;
  }

  return (
    <InsertPin
      handleSubmit={handleSubmit}
      formData={formData}
      handleChange={handleChange}
      error={error}
      loading={loading}
    />
  );
};
export default AdminPIN;
