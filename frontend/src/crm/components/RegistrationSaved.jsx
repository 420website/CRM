import { useNavigate } from "react-router-dom";

export default function RegistrationSaved({ submitStatus, setSubmitStatus }) {
  window.scrollTo({ top: 0, behavior: "smooth" });

  const navigate = useNavigate();

  const goBack = () => {
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-2">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-4 mx-4 text-center">
        <div className="mb-3">
          <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
            <svg
              className="w-6 h-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            Saved for Review!
          </h2>
          <p className="text-gray-600 mb-3">{submitStatus.message}</p>
          {submitStatus.id && (
            <p className="text-sm text-gray-500 mb-3">
              Registration ID: {submitStatus.id}
            </p>
          )}
        </div>
        <div className="flex flex-col gap-3">
          <button
            onClick={() => {
              navigate("/admin-dashboard");
            }}
            className="w-full bg-black text-white py-3 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
          >
            Go to Dashboard
          </button>
          {submitStatus.id && (
            <button
              onClick={() => {
                navigate(`/admin-edit/${submitStatus.id}`);
              }}
              className="w-full bg-black text-white py-3 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
            >
              Go to Patient File
            </button>
          )}
          <div className="flex gap-3">
            <button
              onClick={() => {
                setSubmitStatus(null);
              }}
              className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
            >
              Register Another
            </button>
            <button
              onClick={goBack}
              className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
