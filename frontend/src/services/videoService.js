import api, { apiCall } from "./api";

export const VideoServices = {
  internalJoinVideo: async (patient_id) => {
    return apiCall(
      () => api.post(`/video/join/internal/${patient_id}`),
      "Joining video failed.",
    );
  },
  externalJoinVideo: async (patient_id, user_id, passcode) => {
    return apiCall(
      () =>
        api.post(`/video/join/external/${patient_id}`, {
          passcode: passcode,
          guest_id: user_id,
        }),
      "Joining video failed.",
    );
  },
  deleteSession: async (patient_id) => {
    return apiCall(
      () => api.delete(`/video/delete/${patient_id}`),
      "Delete video session failed.",
    );
  },
  lockSession: async (patient_id) => {
    return apiCall(
      () => api.post(`/video/lock/${patient_id}`),
      "Locking video failed.",
    );
  },
  unlockSession: async (patient_id) => {
    return apiCall(
      () => api.post(`/video/unlock/${patient_id}`),
      "Unlocking session failed.",
    );
  },

  refresh_lease: async (patient_id) => {
    return apiCall(
      () => api.post(`/video/host/poll/${patient_id}`),
      "Failed to refresh lease on session.",
    );
  },
};
