import { createContext, useContext, useEffect, useState } from "react";
import { AuthServices } from "../services/authService";
import { useNavigate } from "react-router-dom";
import { tokenManager } from "../tokenManager";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [userRole, setUserRole] = useState("admin");
  const [userPermissions, setUserPermissions] = useState([]);
  const [isAuthenticatorMfaSetup, setIsAuthenticatorMfaSetup] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [refreshTimer, setRefreshTimer] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [currentRegistrationId, setCurrentRegistrationId] = useState(null);

  const startTokenRefreshCycle = (accessToken, expiresAt) => {
    setIsAuthenticated(true);
    setIsLoggedIn(true);
    tokenManager.setAccessToken(accessToken);

    if (refreshTimer) {
      clearTimeout(refreshTimer);
    }

    const expiry = new Date(expiresAt);
    const now = new Date();
    const timeUntilExpiry = Math.floor((expiry - now) / 1000) - 120;

    if (timeUntilExpiry > 0) {
      const timerId = setTimeout(() => {
        setRefreshTimer(null);
        tryRefresh();
      }, timeUntilExpiry * 1000);

      setRefreshTimer(timerId);
    }
  };

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

  const tryRefresh = async () => {
    if (isRefreshing) {
      return;
    }

    setIsRefreshing(true);

    try {
      const response = await AuthServices.refresh_token();

      if (response.success) {
        setUserRole(response.data?.user_role);
        setUserPermissions(response.data?.user_permissions);

        const { access_token, expires_at } = response.data;
        startTokenRefreshCycle(access_token, expires_at);
      } else {
        if (isAuthenticated) {
          logout();
        }
      }
    } catch (error) {
      logout();
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    // Only run on mount or when refreshTimer is cleared
    if (!refreshTimer) {
      tryRefresh();
    }

    // Cleanup timer on unmount
    return () => {
      if (refreshTimer) {
        clearTimeout(refreshTimer);
      }
    };
  }, [refreshTimer]);

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
        startTokenRefreshCycle,
        currentRegistrationId,
        setCurrentRegistrationId,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
