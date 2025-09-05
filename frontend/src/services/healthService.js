import api, { apiCall } from "./api";

export const HealthServices = {
  check_health: async () => {
    return apiCall(() => api.get("/health"), "Get users failed.");
  },
};
