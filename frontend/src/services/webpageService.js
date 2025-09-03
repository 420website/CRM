import api, { apiCall } from "./api";

export const WebpageServices = {
  send_contact_message: async (data) => {
    return apiCall(
      () => api.post("/my420/contact", data),
      "Sending contact message failed.",
    );
  },
  send_register_message: async (data) => {
    return apiCall(
      () => api.post("/my420/register", data),
      "Sending register message failed.",
    );
  },
  delete_contact_message: async (contactId) => {
    return apiCall(
      () => api.delete(`/my420/contact/${contactId}`),
      "Deleting contact message failed.",
    );
  },

  delete_register_message: async (registrationId) => {
    return apiCall(
      () => api.delete(`/my420/register/${registrationId}`),
      "Deleting registration message failed.",
    );
  },
};
