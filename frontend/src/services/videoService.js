import api, { apiCall } from "./api";

export const VideoServices = {
  // create_session: async () => {
  //   return apiCall(() => api.post("/video/session"), "Create session failed.");
  // },

  internal_join_session: async (patient_id) => {
    return apiCall(
      () => api.post(`/video/session/internal/${patient_id}`),
      "Joining session failed.",
    );
  },

  heartbeat: async (patient_id) => {
    return apiCall(
      () => api.post(`/video/session/heartbeat/${patient_id}`),
      "Heartbeat failed.",
    );
  },

  leave_session: async (patient_id) => {
    return apiCall(
      () => api.post(`/video/session/leave/${patient_id}`),
      "Heartbeat failed.",
    );
  },

  delete_session: async () => {
    return apiCall(() => api.delete("/video/session"), "Delet session failed.");
  },

  exeternal_join_session: async () => {
    return apiCall(
      () => api.get("/video/session/external-join"),
      "Joining session failed.",
    );
  },
};
