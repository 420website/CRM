import axios from "axios";
import { tokenManager } from "../tokenManager";

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

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    config.withCredentials = true;

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
