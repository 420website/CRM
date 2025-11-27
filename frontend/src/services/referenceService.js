import api, { apiCall } from "./api";

export const ReferenceServices = {
  // Reference Options
  create_option: async (type, data) => {
    data = { ...data, type: type };

    return apiCall(
      () => api.post("/reference-data/option", data),
      `Creating ${type} failed.`,
    );
  },

  get_options: async (type) => {
    return apiCall(
      () => api.get(`/reference-data/option/${type}`),
      `Fetching ${type} failed.`,
    );
  },

  delete_option_by_id: async (type, id) => {
    return apiCall(
      () => api.delete(`/reference-data/option/${id}`),
      `Deleting ${type} by ID failed.`,
    );
  },

  delete_option_by_name: async (type, name) => {
    return apiCall(
      () => api.delete(`/reference-data/option/${type}/${name}`),
      `Deleting ${type} by name failed.`,
    );
  },

  update_option: async (type, id, data) => {
    data = { ...data, type: type };

    return apiCall(
      () => api.patch(`/reference-data/option/${id}`, data),
      `Updating ${type} failed.`,
    );
  },

  // Templates
  create_template: async (type, data) => {
    data = { ...data, type: type };

    return apiCall(
      () => api.post("/reference-data/template", data),
      `Creating ${type} failed.`,
    );
  },

  get_templates: async (type) => {
    return apiCall(
      () => api.get(`/reference-data/template/${type}`),
      `Fetching ${type} failed.`,
    );
  },

  delete_template_by_id: async (type, id) => {
    return apiCall(
      () => api.delete(`/reference-data/template/${id}`),
      `Deleting ${type} by ID failed.`,
    );
  },

  delete_template_by_name: async (type, name) => {
    return apiCall(
      () => api.delete(`/reference-data/template/${type}/${name}`),
      `Deleting ${type} by name failed.`,
    );
  },

  update_template: async (type, id, data) => {
    data = { ...data, type: type };

    return apiCall(
      () => api.patch(`/reference-data/template/${id}`, data),
      `Updating ${type} failed.`,
    );
  },
};
