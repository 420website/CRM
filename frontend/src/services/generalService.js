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
  // DOCUMENT TYPE
  // ======================
  create_document_type: async (data) => {
    return apiCall(
      () => api.post("/general/document-type", data),
      "Creating document type failed.",
    );
  },

  get_document_types: async () => {
    return apiCall(
      () => api.get("/general/document-type"),
      "Fetching document type failed.",
    );
  },

  delete_document_type_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/general/document-type/${id}`),
      "Deleting document type by ID failed.",
    );
  },

  delete_document_type_by_name: async (name) => {
    return apiCall(
      () => api.delete(`/general/document-type/by-name/${name}`),
      "Deleting document type by name failed.",
    );
  },

  update_document_type: async (id, data) => {
    return apiCall(
      () => api.patch(`/general/document-type/${id}`, data),
      "Updating document type failed.",
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

  // ======================
  // Medication Templates
  // ======================
  create_medication_template: async (data) => {
    return apiCall(
      () => api.post("/general/medication-template", data),
      "Creating medication templates failed.",
    );
  },

  get_medication_template: async () => {
    return apiCall(
      () => api.get("/general/medication-template"),
      "Fetching medication templates failed.",
    );
  },

  delete_medication_template_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/general/medication-template/${id}`),
      "Deleting medication templates by ID failed.",
    );
  },

  delete_medication_template_by_name: async (name) => {
    return apiCall(
      () => api.delete(`/general/medication-template/by-name/${name}`),
      "Deleting medication templates by name failed.",
    );
  },

  update_medication_template: async (id, data) => {
    return apiCall(
      () => api.patch(`/general/medication-template/${id}`, data),
      "Updating medication templates failed.",
    );
  },
  // ======================
  // Medication outcomes
  // ======================
  create_medication_outcome: async (data) => {
    return apiCall(
      () => api.post("/general/medication-outcome", data),
      "Creating medication outcomes failed.",
    );
  },

  get_medication_outcomes: async () => {
    return apiCall(
      () => api.get("/general/medication-outcome"),
      "Fetching medication outcomes failed.",
    );
  },

  delete_medication_outcome_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/general/medication-outcome/${id}`),
      "Deleting medication outcome by ID failed.",
    );
  },

  delete_medication_outcome_by_name: async (name) => {
    return apiCall(
      () => api.delete(`/general/medication-outcome/by-name/${name}`),
      "Deleting medication outcome by name failed.",
    );
  },

  update_medication_outcome: async (id, data) => {
    return apiCall(
      () => api.patch(`/general/medication-outcome/${id}`, data),
      "Updating medication outcome failed.",
    );
  },
  // ======================
  // Medication Templates
  // ======================
  create_general: async (type, data) => {
    data = { ...data, type: type };

    return apiCall(
      () => api.post("/general/general", data),
      "Creating general failed.",
    );
  },

  get_general_type: async (type) => {
    return apiCall(
      () => api.get(`/general/general/${type}`),
      `Fetching ${type} failed.`,
    );
  },

  delete_general_by_id: async (type, id) => {
    return apiCall(
      () => api.delete(`/general/general/${id}`),
      `Deleting ${type} by ID failed.`,
    );
  },

  delete_general_by_name: async (type, name) => {
    return apiCall(
      () => api.delete(`/general/general/by-name/${type}/${name}`),
      `Deleting ${type} by name failed.`,
    );
  },

  update_general: async (type, id, data) => {
    data = { ...data, type: type };

    return apiCall(
      () => api.patch(`/general/general/${id}`, data),
      `Updating ${type} failed.`,
    );
  },
};
