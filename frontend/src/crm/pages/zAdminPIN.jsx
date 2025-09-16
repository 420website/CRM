import React, { useState } from "react";
import EmailTwoFactorVerify from "../components/EmailTwoFactorVerify";
import { AuthServices } from "../../services/authService";
import { tokenManager } from "../../tokenManager";
import { useAuth } from "../../context/AuthContext";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

function InsertPin({ handleSubmit, formData, handleChange, error, loading }) {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Admin Access
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your PIN to access the admin area
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 text-center"
              >
                10-Digit PIN
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10 sm:text-sm text-center text-2xl tracking-widest"
                  placeholder="Enter your pin"
                />
              </div>
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
  const [email, setEmail] = useState(null);
  const { setIsLoggedIn, setIsAuthenticatorMfaSetup, isAuthenticated } =
    useAuth();
  const [formData, setFormData] = useState({
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

    const result = await AuthServices.login_pin(formData.password);

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
    return <EmailTwoFactorVerify email={email} onCancel={onCancel} />;
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
