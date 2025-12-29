import { useState } from "react";
import { useParams } from "react-router-dom";
import { useGuestAuth } from "../../context/GuestAuthContext";

// utils/guestUtils.js
export const getOrCreateGuestId = (sessionToken) => {
  const storageKey = `guest_id_${sessionToken}`;
  let guestId = sessionStorage.getItem(storageKey);

  if (!guestId) {
    // Generate a unique guest ID that the user never sees
    guestId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem(storageKey, guestId);
  }

  return guestId;
};

export const clearGuestId = (sessionToken) => {
  sessionStorage.removeItem(`guest_id_${sessionToken}`);
};

function GuestVideoAccess() {
  const { patientId } = useParams();
  const [passcode, setPasscode] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { authenticate } = useGuestAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      await authenticate(patientId, passcode);
    } catch (err) {
      setError("Unable to validate passcode. Please try again.");
    } finally {
      setIsLoading(false);
      setPasscode("");
    }
  };

  return (
    <div className="flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h2 className="text-2xl font-bold mb-6 text-center">
          Join Video Session
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter Passcode
            </label>
            <input
              type="text"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your passcode"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? "Validating..." : "Join Session"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default GuestVideoAccess;
