import api, { apiCall } from "./api";

export const GeneralServices = {
  // ======================
  // NOTE TEMPLATE
  // ======================
  create_note_template: async (data) => {
    return apiCall(
      () => api.post("/general/note-template", data),
      "Creating note template failed.",
    );
  },

  get_note_templates: async () => {
    return apiCall(
      () => api.get("/general/note-template"),
      "Fetching note templates failed.",
    );
  },

  delete_note_template_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/general/note-template/${id}`),
      "Deleting note template by ID failed.",
    );
  },

  delete_note_template_by_name: async (name) => {
    return apiCall(
      () => api.delete(`/general/note-template/by-name/${name}`),
      "Deleting note template by name failed.",
    );
  },

  update_note_template: async (id, data) => {
    return apiCall(
      () => api.patch(`/general/note-template/${id}`, data),
      "Updating note template failed.",
    );
  },

  // ======================
  // CLINICAL TEMPLATE
  // ======================
  create_clinical_template: async (data) => {
    return apiCall(
      () => api.post("/general/clinical-template", data),
      "Creating clinical template failed.",
    );
  },

  get_clinical_templates: async () => {
    return apiCall(
      () => api.get("/general/clinical-template"), // note typo in backend route!
      "Fetching clinical templates failed.",
    );
  },

  delete_clinical_template_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/general/clinical-template/${id}`),
      "Deleting clinical template by ID failed.",
    );
  },

  delete_clinical_template_by_name: async (name) => {
    return apiCall(
      () => api.delete(`/general/clinical-template/by-name/${name}`),
      "Deleting clinical template by name failed.",
    );
  },

  update_clinical_template: async (id, data) => {
    return apiCall(
      () => api.patch(`/general/clinical-template/${id}`, data),
      "Updating clinical template failed.",
    );
  },

  // ======================
  // DISPOSITION
  // ======================
  create_disposition: async (data) => {
    return apiCall(
      () => api.post("/general/disposition", data),
      "Creating disposition failed.",
    );
  },

  get_dispositions: async () => {
    return apiCall(
      () => api.get("/general/disposition"),
      "Fetching dispositions failed.",
    );
  },

  delete_disposition_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/general/disposition/${id}`),
      "Deleting disposition by ID failed.",
    );
  },

  delete_disposition_by_name: async (name) => {
    return apiCall(
      () => api.delete(`/general/disposition/by-name/${name}`),
      "Deleting disposition by name failed.",
    );
  },

  update_disposition: async (id, data) => {
    return apiCall(
      () => api.patch(`/general/disposition/${id}`, data),
      "Updating disposition failed.",
    );
  },

  // ======================
  // REFERRAL SITE
  // ======================
  create_referral_site: async (data) => {
    return apiCall(
      () => api.post("/general/referral-site", data),
      "Creating referral site failed.",
    );
  },

  get_referral_sites: async () => {
    return apiCall(
      () => api.get("/general/referral-site"),
      "Fetching referral sites failed.",
    );
  },

  delete_referral_site_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/general/referral-site/${id}`),
      "Deleting referral site by ID failed.",
    );
  },

  delete_referral_site_by_name: async (name) => {
    return apiCall(
      () => api.delete(`/general/referral-site/by-name/${name}`),
      "Deleting referral site by name failed.",
    );
  },

  update_referral_site: async (id, data) => {
    return apiCall(
      () => api.patch(`/general/referral-site/${id}`, data),
      "Updating referral site failed.",
    );
  },
};
