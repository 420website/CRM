import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Initial authentication state
const initialState = {
  isAuthenticated: false,
  is2FAComplete: false,
  user: null,
  sessionToken: null,
  permissions: {},
  loading: true,
  error: null
};

// Action types
const AUTH_ACTIONS = {
  LOADING: 'LOADING',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  SET_2FA_PENDING: 'SET_2FA_PENDING',
  COMPLETE_2FA: 'COMPLETE_2FA',
  UPDATE_USER: 'UPDATE_USER',
  UPDATE_PERMISSIONS: 'UPDATE_PERMISSIONS',
  SET_SESSION_TOKEN: 'SET_SESSION_TOKEN',
  LOGOUT: 'LOGOUT',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  RESTORE_SESSION: 'RESTORE_SESSION'
};

// Auth reducer to manage state transitions
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOADING:
      return {
        ...state,
        loading: action.payload,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        isAuthenticated: true,
        is2FAComplete: false,
        user: action.payload.user,
        sessionToken: action.payload.sessionToken,
        permissions: action.payload.permissions || {},
        loading: false,
        error: null
      };

    case AUTH_ACTIONS.SET_2FA_PENDING:
      return {
        ...state,
        isAuthenticated: true,
        is2FAComplete: false,
        user: action.payload.user,
        sessionToken: action.payload.sessionToken,
        loading: false,
        error: null
      };

    case AUTH_ACTIONS.COMPLETE_2FA:
      return {
        ...state,
        is2FAComplete: true,
        sessionToken: action.payload.sessionToken,
        loading: false,
        error: null
      };

    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
        error: null
      };

    case AUTH_ACTIONS.UPDATE_PERMISSIONS:
      return {
        ...state,
        permissions: { ...state.permissions, ...action.payload },
        error: null
      };

    case AUTH_ACTIONS.SET_SESSION_TOKEN:
      return {
        ...state,
        sessionToken: action.payload,
        error: null
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState,
        loading: false
      };

    case AUTH_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    case AUTH_ACTIONS.RESTORE_SESSION:
      return {
        ...state,
        isAuthenticated: action.payload.isAuthenticated,
        is2FAComplete: action.payload.is2FAComplete,
        user: action.payload.user,
        sessionToken: action.payload.sessionToken,
        permissions: action.payload.permissions,
        loading: false,
        error: null
      };

    default:
      return state;
  }
};

// Create Auth Context
const AuthContext = createContext();

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Restore authentication state from localStorage on app start
  useEffect(() => {
    const restoreAuthState = () => {
      try {
        dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });

        // Check localStorage for persisted auth state
        const persistedAuth = localStorage.getItem('auth_state');
        const adminAuthenticated = localStorage.getItem('admin_authenticated');
        const currentUser = localStorage.getItem('current_user');

        if (persistedAuth) {
          const authData = JSON.parse(persistedAuth);
          // Validate that the data structure is correct
          if (authData.user && authData.sessionToken) {
            dispatch({
              type: AUTH_ACTIONS.RESTORE_SESSION,
              payload: {
                isAuthenticated: true,
                is2FAComplete: authData.is2FAComplete || true,
                user: authData.user,
                sessionToken: authData.sessionToken,
                permissions: authData.permissions || {}
              }
            });
            return;
          }
        }

        // Fallback: check legacy sessionStorage and migrate
        if (adminAuthenticated === 'true' && currentUser) {
          const userData = JSON.parse(currentUser);
          const authState = {
            isAuthenticated: true,
            is2FAComplete: true,
            user: userData,
            sessionToken: userData.sessionToken || null,
            permissions: userData.permissions || {}
          };

          // Save to localStorage for future use
          localStorage.setItem('auth_state', JSON.stringify(authState));
          
          // Clear sessionStorage
          sessionStorage.removeItem('admin_authenticated');
          sessionStorage.removeItem('current_user');

          dispatch({
            type: AUTH_ACTIONS.RESTORE_SESSION,
            payload: authState
          });
          return;
        }

        // No valid auth state found
        dispatch({ type: AUTH_ACTIONS.LOADING, payload: false });

      } catch (error) {
        console.error('Error restoring auth state:', error);
        dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: 'Failed to restore authentication state' });
      }
    };

    restoreAuthState();
  }, []);

  // Persist auth state to localStorage whenever it changes
  useEffect(() => {
    if (!state.loading && state.isAuthenticated && state.user) {
      const authState = {
        isAuthenticated: state.isAuthenticated,
        is2FAComplete: state.is2FAComplete,
        user: state.user,
        sessionToken: state.sessionToken,
        permissions: state.permissions
      };
      localStorage.setItem('auth_state', JSON.stringify(authState));
    } else if (!state.loading && !state.isAuthenticated) {
      localStorage.removeItem('auth_state');
      localStorage.removeItem('admin_authenticated');
      localStorage.removeItem('current_user');
    }
  }, [state.isAuthenticated, state.is2FAComplete, state.user, state.sessionToken, state.permissions, state.loading]);

  // Auth actions
  const login = (userData, sessionToken) => {
    dispatch({
      type: AUTH_ACTIONS.LOGIN_SUCCESS,
      payload: {
        user: userData,
        sessionToken,
        permissions: userData.permissions || {}
      }
    });
  };

  const set2FAPending = (userData, sessionToken) => {
    dispatch({
      type: AUTH_ACTIONS.SET_2FA_PENDING,
      payload: {
        user: userData,
        sessionToken
      }
    });
  };

  const complete2FA = (sessionToken) => {
    dispatch({
      type: AUTH_ACTIONS.COMPLETE_2FA,
      payload: { sessionToken }
    });
  };

  const updateUser = (userData) => {
    dispatch({
      type: AUTH_ACTIONS.UPDATE_USER,
      payload: userData
    });
  };

  const updatePermissions = (permissions) => {
    dispatch({
      type: AUTH_ACTIONS.UPDATE_PERMISSIONS,
      payload: permissions
    });
  };

  const setSessionToken = (token) => {
    dispatch({
      type: AUTH_ACTIONS.SET_SESSION_TOKEN,
      payload: token
    });
  };

  const logout = () => {
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
  };

  const setError = (error) => {
    dispatch({
      type: AUTH_ACTIONS.SET_ERROR,
      payload: error
    });
  };

  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  const setLoading = (loading) => {
    dispatch({
      type: AUTH_ACTIONS.LOADING,
      payload: loading
    });
  };

  // Helper functions
  const isAdmin = () => {
    return state.user?.user_id === "admin" && state.user?.user_type === "admin";
  };

  const hasTabPermissions = () => {
    // Admin always has all permissions
    if (isAdmin()) {
      return true;
    }

    // Check if user has any tab permissions
    const tabPermissions = ['Client', 'Tests', 'Medication', 'Dispensing', 'Notes', 'Activities', 'Interactions', 'Attachments'];
    return tabPermissions.some(tab => state.permissions[tab] === true);
  };

  const hasPermission = (permission) => {
    // Admin has all permissions
    if (isAdmin()) {
      return true;
    }
    return state.permissions[permission] === true;
  };

  // Check if fully authenticated (both PIN and 2FA complete)
  const isFullyAuthenticated = () => {
    return state.isAuthenticated && state.is2FAComplete;
  };

  const value = {
    // State
    ...state,
    
    // Actions
    login,
    set2FAPending,
    complete2FA,
    updateUser,
    updatePermissions,
    setSessionToken,
    logout,
    setError,
    clearError,
    setLoading,
    
    // Helper functions
    isAdmin,
    hasTabPermissions,
    hasPermission,
    isFullyAuthenticated
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;