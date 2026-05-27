import { createContext, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { VideoServices } from "../services/videoService";
import toast from "react-hot-toast";

const GuestAuthContext = createContext();

export const useGuestAuth = () => {
  const context = useContext(GuestAuthContext);
  if (!context) {
    throw new Error("useGuestAuth must be used within GuestAuthProvider");
  }
  return context;
};

export function GuestAuthProvider({ children }) {
  const navigate = useNavigate();

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [guestData, setGuestData] = useState(null);
  const [sessionJWT, setSessionJWT] = useState(null);
  const [sessionPasscode, setSessionPasscode] = useState(null);
  const [sessionName, setSessionName] = useState(null);

  const getOrCreateGuestId = (sessionToken) => {
    const storageKey = `guest_id_${sessionToken}`;
    let guestId = sessionStorage.getItem(storageKey);

    // Generate a unique guest ID that the user never sees
    if (!guestId) {
      guestId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem(storageKey, guestId);
    }

    return guestId;
  };

  const clearGuestId = (sessionToken) => {
    sessionStorage.removeItem(`guest_id_${sessionToken}`);
  };

  // Authenticate guest with passcode
  const authenticate = async (patientId, passcode) => {
    try {
      const guestId = getOrCreateGuestId(patientId);

      // Validate passcode with your backend
      const response = await VideoServices.externalJoinVideo(
        patientId,
        guestId,
        passcode,
      );

      if (!response.success || !response.data) {
        throw new Error(response.message || "Failed to get session token");
      }

      const { access_token, sessionName, sessionPasscode } = response.data;
      setSessionJWT(access_token);
      setSessionName(sessionName);
      setSessionPasscode(sessionPasscode);
      setIsAuthenticated(true);

      sessionStorage.setItem(`guest_auth_${patientId}`, guestId);

      // Navigate to preview page
      navigate(`/crm/guest-preview/${patientId}`);

      return true;
    } catch (err) {
      const errorMessage = err.message || err.toString();
      toast.error(errorMessage);
      return false;
    }
  };

  // Logout and clear session
  const logout = () => {
    if (token) {
      sessionStorage.removeItem(`guest_auth_${token}`);
    }
    setIsAuthenticated(false);
    setGuestData(null);
    navigate(`/crm/guest-video/${token}`);
  };

  // Get stored guest data for rejoining Zoom
  const getGuestData = () => {
    if (!token) return null;

    const stored = sessionStorage.getItem(`guest_auth_${token}`);
    if (!stored) return null;

    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  };

  const value = {
    isAuthenticated,
    isCheckingAuth,
    guestData,
    authenticate,
    logout,
    getGuestData,
    sessionJWT,
    sessionPasscode,
    sessionName,
  };

  return (
    <GuestAuthContext.Provider value={value}>
      {children}
    </GuestAuthContext.Provider>
  );
}
