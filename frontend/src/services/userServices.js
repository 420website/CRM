import api, { apiCall } from "./api";

export const UserServices = {
  get_users: async () => {
    return apiCall(() => api.get("/auth/users"), "Get users failed.");
  },

  create_user: async (data) => {
    return apiCall(() => api.post("/auth/users", data), "Create user failed.");
  },

  delete_user: async (id) => {
    return apiCall(
      () => api.delete(`/auth/users/${id}`),
      "Delete user failed.",
    );
  },

  update_user: async (id, data) => {
    return apiCall(
      () => api.patch(`/auth/users/${id}`, data),
      "Updating user failed.",
    );
  },
};
