import { useEffect, useState } from "react";
import { AuthServices } from "../../services/authService";
import { useNavigate, useSearchParams } from "react-router-dom";

export function SuccessfullyVerified() {
  const navigate = useNavigate();

  return (
    <div className="bg-white py-8 px-6 shadow rounded-lg sm:px-10 flex flex-col items-center space-y-6">
      <h2 className="text-2xl font-bold text-center text-black-700 mb-0">
        Email Verified
      </h2>
      <p className="text-sm text-gray-600 text-center">
        Your email has been verified.
      </p>

      <button
        type="button"
        onClick={() => navigate("/admin-pin")}
        className="w-full py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
      >
        Go to Login
      </button>
    </div>
  );
}

function UnsuccessfullyVerified() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const sendEmail = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      await AuthServices.send_verification_email(email);
    } catch (err) {
      console.error("Verification resend error:", err);
    } finally {
      // Always show the same generic success-style message
      setMessage("If the email is valid, a verification link has been sent.");
      setLoading(false);
    }
  };

  return (
    <div className="bg-white py-8 px-6 shadow rounded-lg sm:px-10 flex flex-col items-center space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-center text-black-600">
          Verify Email
        </h2>
        <p className="text-sm text-gray-600 text-center">
          Enter your email to send the verification link.
        </p>
      </div>

      <form className="w-full space-y-4" onSubmit={sendEmail}>
        <div>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="Email"
            maxLength="50"
            disabled={loading}
            className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black sm:text-sm"
          />
        </div>
        {message && (
          <div className="bg-gray-50 border border-gray-200 text-gray-700 px-4 py-2 rounded text-sm text-center">
            {message}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded text-sm text-center">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
        >
          {loading ? "Sending..." : "Send Email"}
        </button>
      </form>
    </div>
  );
}

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const [result, setResult] = useState(false);
  const token = searchParams.get("token");

  useEffect(() => {
    const verify_email = async () => {
      const response = await AuthServices.verify_email(token);

      if (response.success) {
        setResult(true);
      } else {
        setResult(false);
      }
    };
    verify_email();
  }, []);

  return (
    <div className="lg:h-[calc(100vh-400px)] bg-gray-50 flex flex-col justify-center mx-4 my-12">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="auth-header">
          {result ? <SuccessfullyVerified /> : <UnsuccessfullyVerified />}
        </div>
      </div>
    </div>
  );
}
