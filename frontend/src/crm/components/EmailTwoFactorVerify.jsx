import { useState, useEffect } from "react";
import { AuthServices } from "../../services/authService";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

function InputScreen({
  email,
  timeLeft,
  handleVerify,
  code,
  setCode,
  sendingCode,
  error,
  loading,
  send_code,
  setShowInputScreen,
  formatTime,
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Enter Verification Code
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter the 6-digit code sent to {email}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              {error}
            </div>
          )}

          {timeLeft > 0 && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-green-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-green-800">
                    Code expires in <strong>{formatTime(timeLeft)}</strong>
                  </p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleVerify} className="space-y-6">
            <div>
              <label
                htmlFor="email-code"
                className="block text-sm font-medium text-gray-700 text-center"
              >
                6-digit verification code
              </label>
              <div className="mt-1">
                <input
                  id="email-code"
                  type="text"
                  maxLength="6"
                  pattern="[0-9]*"
                  inputMode="numeric"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10 sm:text-sm text-center text-2xl tracking-widest font-mono"
                  placeholder="000000"
                  autoComplete="one-time-code"
                />
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setShowInputScreen(false)}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading || code.length !== 6}
                className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black disabled:bg-gray-300"
              >
                {loading ? "Verifying..." : "Verify"}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={send_code}
                disabled={sendingCode || timeLeft > 0}
                className="text-sm text-gray-600 hover:text-gray-800 underline disabled:text-gray-400 disabled:no-underline"
              >
                {sendingCode
                  ? "Sending..."
                  : timeLeft > 0
                    ? `Request new code in ${formatTime(timeLeft)}`
                    : "Resend verification code"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

function LandingScreen({
  email,
  timeLeft,
  setShowInputScreen,
  onCancel,
  error,
  formatTime,
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center mb-6">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-4">
              <svg
                className="h-6 w-6 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900">
              Verification Code Sent
            </h3>
            <p className="text-sm text-gray-600 mt-2">
              A 6-digit verification code has been sent to:
            </p>
            <p className="text-sm font-medium text-gray-900 mt-1">
              📧 <strong>{email}</strong>
            </p>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-gray-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="ml-3 text-sm text-gray-600">
                <p className="font-medium text-gray-900 mb-1">Next Steps:</p>
                <ul className="space-y-1">
                  <li>• Check {email} for a 6-digit verification code</li>
                  <li>• Enter the code in the next screen to complete setup</li>
                  <li>
                    • Codes expire after 1 minute for security{" "}
                    {timeLeft > 0 && `(${formatTime(timeLeft)} remaining)`}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              {error}
            </div>
          )}

          <div className="flex space-x-4">
            <button
              onClick={onCancel}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowInputScreen(true);
              }}
              className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
            >
              Enter Verification Code
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const EmailTwoFactorVerify = ({ email, onCancel }) => {
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { startTokenRefreshCycle } = useAuth();
  const [sendingCode, setSendingCode] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [showInputScreen, setShowInputScreen] = useState(false);
  const { setUserRole, setUserPermissions } = useAuth();

  async function send_email() {
    const result = await AuthServices.send_mfa_email();
    if (result.success) {
      setTimeLeft(60);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Failed to send mfa verification email.");
      }
    }
  }

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  useEffect(() => {
    async function fetchMFAEmail() {
      setLoading(true);
      await send_email();
      setLoading(false);
    }
    fetchMFAEmail();
  }, []);

  // Countdown timer
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (!code || code.length !== 6) {
      setError("Please enter the 6-digit verification code");
      return;
    }

    const result = await AuthServices.verify_email_mfa(code);

    if (result.success) {
      startTokenRefreshCycle(
        result.data?.access_token,
        result.data?.expires_at,
      );
      setUserRole(result.data?.user_role);
      setUserPermissions(result.data?.user_permissions);
      navigate("/admin-menu");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid code.");
      } else {
        setError("MFA not verified. Please try again.");
      }
    }
    setLoading(false);
  };

  // Show input screen after user clicks "Enter Verification Code"
  if (showInputScreen) {
    return (
      <InputScreen
        email={email}
        timeLeft={timeLeft}
        handleVerify={handleVerify}
        code={code}
        setCode={setCode}
        sendingCode={sendingCode}
        error={error}
        loading={loading}
        send_code={send_email}
        setShowInputScreen={setShowInputScreen}
        formatTime={formatTime}
      />
    );
  } else {
    return (
      <LandingScreen
        email={email}
        timeLeft={timeLeft}
        setShowInputScreen={setShowInputScreen}
        onCancel={onCancel}
        error={error}
        formatTime={formatTime}
      />
    );
  }
};
export default EmailTwoFactorVerify;
