import api, { apiCall } from "./api";

export const AnalyticsServices = {
  get_legacy_data: async () => {
    return apiCall(
      () => api.get("/analytics/legacy-data-summary"),
      "Getting legacy data failed.",
    );
  },

  clear_legacy_data: async () => {
    return apiCall(
      () => api.delete("/analytics/legacy-data-summary"),
      "Deleting legacy data failed.",
    );
  },

  upload_legacy_data: async (data) => {
    return apiCall(
      () =>
        api.post("/analytics/upload-legacy-data", data, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }),
      "Uploading legacy data failed.",
    );
  },

  prompt_claude: async (data) => {
    return apiCall(
      () => api.post("/analytics/claude-chat", data),
      "Prompting claude chat failed.",
    );
  },
};
