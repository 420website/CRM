import axios from "axios";
import { tokenManager } from "../tokenManager";
import { AuthServices } from "../services/authService";

const BASE_URL =
  typeof import.meta !== "undefined" && import.meta.env
    ? import.meta.env?.VITE_API_BASE_URL
    : process.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Track refresh state to prevent multiple simultaneous refresh calls
let isRefreshing = false;
let failedQueue = [];

// Process queued requests after token refresh
const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor to proactively renew and add access token
api.interceptors.request.use(
  async (config) => {
    config.withCredentials = true;

    // Skip token checks for:
    // 1. Auth endpoints
    // 2. Share link GET endpoints
    const isAuthEndpoint = config.url?.includes("/auth");
    const isShareLinkGet =
      config.url?.includes("/share-link/") &&
      config.method?.toLowerCase() === "get";

    const shouldSkipRefresh = isAuthEndpoint || isShareLinkGet;

    if (!shouldSkipRefresh && tokenManager.expiresSoon(2)) {
      if (!isRefreshing) {
        isRefreshing = true;

        try {
          const response = await AuthServices.refresh_token();

          if (response.success) {
            const { access_token, expires_at } = response.data;
            tokenManager.setAccessToken(access_token);
            tokenManager.setExpiresAt(expires_at);
            processQueue(null, access_token);
          }
        } catch (error) {
          processQueue(error, null);
        } finally {
          isRefreshing = false;
        }
      } else {
        // Wait for the ongoing refresh to complete
        // Freezes requests until refresh token is returned
        await new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        });
      }
    }
    const token = tokenManager.getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// // Request interceptor to add auth token
// api.interceptors.request.use(
//   (config) => {
//     config.withCredentials = true;
//
//     const token = tokenManager.getAccessToken();
//
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   },
// );

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Skip token refresh for these endpoints:
    // 1. Auth endpoints (login, register, etc.)
    // 2. Share link GET endpoints (use their own token)
    const isAuthEndpoint = originalRequest.url?.includes("/auth");
    const isShareLinkGet =
      originalRequest.url?.includes("/share-link/") &&
      originalRequest.method?.toLowerCase() === "get";

    const shouldSkipRefresh = isAuthEndpoint || isShareLinkGet;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !shouldSkipRefresh
    ) {
      if (isRefreshing) {
        // Queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = "Bearer " + token;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await AuthServices.refresh_token();
        const { access_token } = response.data;
        tokenManager.setAccessToken(access_token);
        processQueue(null, access_token);
        originalRequest.headers["Authorization"] = "Bearer " + access_token;
        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        logout();
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

// Generic API call wrapper with consistent response format
export const apiCall = async (axiosCall, customErrorMessage = null) => {
  try {
    const response = await axiosCall();

    return {
      headers: response.headers,
      success: true,
      data: response.data || {},
    };
  } catch (error) {
    return {
      success: false,
      status: error.response?.status,
      message:
        error.response?.data?.detail ||
        customErrorMessage ||
        "An error occurred.",
      errors: error.response?.data?.errors || {},
    };
  }
};

export default api;
