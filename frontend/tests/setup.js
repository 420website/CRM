import api, { apiCall } from "../src/services/api";

export const TestServices = {
  createVerifiedUser: async (email, password) => {
    return apiCall(
      () =>
        api.post("/testing/register", {
          email,
          password,
        }),
      "Error Registrating testing user.",
    );
  },
  create_user: async (data) => {
    return apiCall(
      () => api.post("/testing/users", data),
      "Create user failed.",
    );
  },

  send_email_mfa: async (email) => {
    return apiCall(
      () =>
        api.post(`/testing/send-mfa-email`, {
          email,
        }),
      "Send verification failed.",
    );
  },

  send_verification_email: async (email) => {
    return apiCall(
      () =>
        api.post(`/testing/send-verfication`, {
          email,
        }),
      "Send verification failed.",
    );
  },

  forgot_password: async (email) => {
    return apiCall(
      () =>
        api.post(`/testing/forgot-password`, {
          email,
        }),
      "Forgot Password failed.",
    );
  },

  deleteUser: async (email, password) => {
    return apiCall(
      () =>
        api.post("/testing/delete-user", {
          email,
          password,
        }),
      "Error testing delete user.",
    );
  },

  get_user: async () => {
    return apiCall(() => {
      (api.get("/testing/me"), "Error getting test user.");
    });
  },
  send_contact_message: async (data) => {
    return apiCall(
      () => api.post("/testing/contact-message", data),
      "Sending contact message failed.",
    );
  },
  send_register_message: async (data) => {
    return apiCall(
      () => api.post("/testing/register-message", data),
      "Sending register message failed.",
    );
  },
};
