import api, { apiCall } from "./api";

export const AuthServices = {
  get_users: async () => {
    return apiCall(() => api.get("/auth/users"), "Get users failed.");
  },

  register: async (email, password) => {
    return apiCall(
      () =>
        api.post("/auth/register", {
          email,
          password,
        }),
      "Registration failed.",
    );
  },

  send_verification_email: async (email) => {
    return apiCall(
      () =>
        api.post("/auth/send-verification", {
          email,
        }),
      "Sending verification email failed.",
    );
  },

  verify_email: async (token) => {
    return apiCall(
      () => api.post(`/auth/verify-email?token=${token}`),
      "Verify Email failed.",
    );
  },

  login: async (email, password) => {
    return apiCall(
      () =>
        api.post("/auth/login", {
          email,
          password,
        }),
      "Login failed.",
    );
  },

  login_pin: async (password) => {
    return apiCall(
      () =>
        api.post("/auth/login-pin", {
          password,
        }),
      "Login failed.",
    );
  },

  forgot_password: async (email) => {
    return apiCall(
      () =>
        api.post(`/auth/forgot-password`, {
          email,
        }),
      "Forgot Password failed.",
    );
  },

  reset_password: async (token, new_password) => {
    return apiCall(
      () =>
        api.post(`/auth/reset-password`, {
          token,
          new_password,
        }),
      "Verify Email failed.",
    );
  },

  send_mfa_email: async () => {
    return apiCall(
      () => api.post("/auth/send-email-mfa-code", {}),
      "Sending mfa email failed.",
    );
  },

  setup_authenticator_mfa: async () => {
    return apiCall(
      () => api.post("/auth/setup-authenticator-mfa"),
      "Setup-mfa failed.",
    );
  },

  verify_authenticator_mfa: async (code) => {
    return apiCall(
      () =>
        api.post("/auth/verify-authenticator-mfa", {
          code,
        }),
      "Verify-mfa failed.",
    );
  },

  verify_email_mfa: async (code) => {
    return apiCall(
      () =>
        api.post("/auth/verify-email-mfa", {
          code,
        }),
      "Verify-mfa failed.",
    );
  },

  verify_recovery_code: async (code) => {
    return apiCall(
      () =>
        api.post("/auth/verify-recovery-code", {
          code,
        }),
      "Verify-mfa failed.",
    );
  },

  regenerate_recovery_codes: async () => {
    return apiCall(
      () => api.post("/auth/regenerate-recovery-codes"),
      "Recovery codes regeneration failed..",
    );
  },

  disable_authenticator_mfa: async (code) => {
    return apiCall(
      () =>
        api.post("/auth/disable-authenticator-mfa", {
          code,
        }),
      "Verify-mfa failed.",
    );
  },

  refresh_token: async () => {
    return apiCall(() => api.post("/auth/refresh"), "Refresh failed.");
  },

  logout: async () => {
    return apiCall(() => api.post("/auth/logout", {}), "Logout failed.");
  },
};
