import api, { apiCall } from "./api";

export const ObjectServices = {
  // ======================
  // Photos
  // ======================
  upload_photo: async (patient_id, name, file) => {
    const formData = new FormData();
    formData.append("file", file);

    return apiCall(
      () =>
        api.post(`/objects/photos/${patient_id}/${name}`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }),
      "Creating photo failed.",
    );
  },

  get_photo_raw: async (patient_id) => {
    return apiCall(
      () =>
        api.get(`/objects/photos/${patient_id}`, {
          responseType: "arraybuffer",
        }),
      "Fetching patient photo failed.",
    );
  },

  delete_photo: async (patient_id) => {
    return apiCall(
      () => api.delete(`/objects/photos/${patient_id}`),
      "Deleting photo failed.",
    );
  },
  // ======================
  // Attachment
  // ======================
  upload_attachment: async (patient_id, file, document_type) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("file_name", file.name);
    formData.append("file_size", file.size);
    formData.append("mime_type", file.type);
    formData.append("document_type", document_type);

    return apiCall(
      () =>
        api.post(`/objects/attachments/${patient_id}`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }),
      "Creating attachment failed.",
    );
  },

  get_attachments_by_patient: async (patient_id) => {
    return apiCall(
      () => api.get(`/objects/attachments/${patient_id}`),
      "Fetching attachments by patient failed.",
    );
  },

  get_attachment_raw: async (file_type) => {
    return apiCall(
      () =>
        api.get(`/objects/attachments/${file_type}`, {
          responseType: "arraybuffer",
        }),
      "Fetching attachment by ID failed.",
    );
  },

  delete_attachment: async (file_key) => {
    return apiCall(
      () => api.delete(`/objects/attachments/${file_key}`),
      "Deleting attachment failed.",
    );
  },
};
