import api, { apiCall } from "./api";

export const VideoServices = {
  syncParticipants: async (patient_id, passcode, participants) => {
    return apiCall(
      () =>
        api.post(`/video/sync/${patient_id}`, {
          session_key: passcode,
          zoom_participants: participants,
        }),
      "Syncing participants failed.",
    );
  },
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
      "Unlocking session failed..",
    );
  },

  //-- Old --

  // internal_join_session: async (patient_id) => {
  //   return apiCall(
  //     () => api.post(`/video/session/internal/${patient_id}`),
  //     "Joining session failed.",
  //   );
  // },
  //
  // heartbeat: async (patient_id) => {
  //   return apiCall(
  //     () => api.post(`/video/session/heartbeat/${patient_id}`),
  //     "Heartbeat failed.",
  //   );
  // },
  //
  // leave_session: async (patient_id) => {
  //   return apiCall(
  //     () => api.post(`/video/session/leave/${patient_id}`),
  //     "Heartbeat failed.",
  //   );
  // },
  //
  // delete_session: async () => {
  //   return apiCall(
  //     () => api.delete("/video/session"),
  //     "Delete session failed.",
  //   );
  // },
  //
  // guest_join_session: async (patient_id, request) => {
  //   return apiCall(
  //     () => api.post(`/video/session/guest/${patient_id}`, request),
  //     "Joining session failed.",
  //   );
  // },
  //
  // guest_heartbeat: async (patient_id, guest_id) => {
  //   return apiCall(
  //     () =>
  //       api.post(`/video/session/guest/heartbeat/${patient_id}/${guest_id}`),
  //     "Heartbeat failed.",
  //   );
  // },
  //
  // guest_leave_session: async (patient_id, guest_id) => {
  //   return apiCall(
  //     () => api.post(`/video/session/guest/leave/${patient_id}/${guest_id}`),
  //     "Heartbeat failed.",
  //   );
  // },
};
