import { createContext, useContext, useEffect, useState } from "react";
import { AuthServices } from "../services/authService";
import { useNavigate } from "react-router-dom";
import { tokenManager } from "../tokenManager";
import { UserServices } from "../services/userServices";
import toast from "react-hot-toast";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [userRole, setUserRole] = useState("admin");
  const [userPermissions, setUserPermissions] = useState([]);
  const [userProvince, setUserProvince] = useState("");
  const [userLocationPermissions, setUserLocationPermissions] = useState([]);
  const [isAuthenticatorMfaSetup, setIsAuthenticatorMfaSetup] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [refreshTimer, setRefreshTimer] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(false);

  const [currentRegistrationId, setCurrentRegistrationId] = useState(null);

  const logout = async () => {
    await AuthServices.logout();
    tokenManager.setAccessToken(null);
    setIsAuthenticated(false);
    setIsLoggedIn(false);
    setIsAuthenticatorMfaSetup(false);
    setRefreshTimer(null);
    setIsRefreshing(false);
    navigate("/");
  };

  const handleAuthenticated = async (accessToken, expiresAt) => {
    tokenManager.setAccessToken(accessToken);
    tokenManager.setExpiresAt(expiresAt); // Store expiry time

    await getPermissions();

    setIsAuthenticated(true);
    setIsLoggedIn(true);
    setIsCheckingAuth(false);
  };

  const tryRefresh = async () => {
    if (isRefreshing) {
      return;
    }
    setIsRefreshing(true);
    setIsCheckingAuth(true);
    try {
      const response = await AuthServices.refresh_token();

      if (response.success) {
        const { access_token, expires_at } = response.data;
        await handleAuthenticated(access_token, expires_at);
      } else {
        if (isAuthenticated) {
          logout();
        }
      }
    } catch (error) {
      if (isAuthenticated) {
        logout();
      }
    } finally {
      setIsRefreshing(false);
      setIsCheckingAuth(false);
    }
  };

  const getPermissions = async () => {
    try {
      const response = await UserServices.get_permissions();

      if (response.success) {
        setUserRole(response.data?.user_role);
        setUserPermissions(response.data?.user_permissions);
        setUserProvince(response.data?.province);
        setUserLocationPermissions(response.data?.location_permissions);
      }
    } catch (error) {
      toast.error("Error getting user permissions");
    }
  };

  useEffect(() => {
    // Initial refresh on mount
    tryRefresh();

    // Handle logout events from interceptor
    const handleLogout = () => {
      logout();
    };

    // Refresh when user returns to screen
    const handleVisibilityChange = () => {
      if (
        document.visibilityState === "visible" &&
        tokenManager.expiresSoon(5)
      ) {
        tryRefresh();
      }
    };

    window.addEventListener("auth:logout", handleLogout);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("focus", handleVisibilityChange);

    return () => {
      window.removeEventListener("auth:logout", handleLogout);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("focus", handleVisibilityChange);
    };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isLoggedIn,
        setIsLoggedIn,
        isAuthenticated,
        setIsAuthenticatorMfaSetup,
        isAuthenticatorMfaSetup,
        logout,
        userRole,
        setUserRole,
        userPermissions,
        setUserPermissions,
        currentRegistrationId,
        setCurrentRegistrationId,
        userProvince,
        userLocationPermissions,
        getPermissions,
        handleAuthenticated,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
