import api, { apiCall } from "./api";

export const PatientServices = {
  // ======================
  // PATIENT
  // ======================
  create_patient: async (data) => {
    return apiCall(
      () => api.post("/patients", data),
      "Creating patient failed.",
    );
  },
  get_patients: async () => {
    return apiCall(() => api.get("/patients"), "Fetching patients failed.");
  },

  get_patients_by_location: async (locations) => {
    return apiCall(
      () => api.get("/patients", { params: { locations: locations } }),
      "Fetching patients failed.",
    );
  },
  get_patient_by_id: async (id) => {
    return apiCall(
      () => api.get(`/patients/${id}`),
      "Fetching patient by ID failed.",
    );
  },
  delete_patient_by_id: async (id) => {
    return apiCall(
      () => api.delete(`/patients/${id}`),
      "Deleting patient by ID failed.",
    );
  },
  delete_patient_by_name: async (first_name, last_name) => {
    return apiCall(
      () => api.delete(`/patients/by-name/${first_name}/${last_name}`),
      "Deleting patient by name failed.",
    );
  },
  update_patient: async (id, data) => {
    return apiCall(
      () => api.patch(`/patients/${id}`, data),
      "Updating patient failed.",
    );
  },

  update_patient_status: async (id, data) => {
    return apiCall(
      () => api.patch(`/patients/${id}/status`, data),
      "Updating patient failed.",
    );
  },

  check_identity_exists: async (data) => {
    return apiCall(
      () => api.post(`/patients/identity/verify`, data),
      "Verifying name and dob failed.",
    );
  },

  check_healthcard_exists: async (data) => {
    return apiCall(
      () => api.post(`/patients/healthcard/verify`, data),
      "Verifying healthcard failed.",
    );
  },

  // ======================
  // Assessment
  // ======================

  // Create a test for a patient
  create_assessment: async (patient_id, data) => {
    return apiCall(
      () => api.post(`/patients/${patient_id}/assessment/`, data),
      "Creating assessment failed.",
    );
  },

  // Get all tests for a patient
  get_assessments_by_patient: async (patient_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/assessments/`),
      "Fetching assessments by patient failed.",
    );
  },

  // Get a specific test by ID for a patient
  get_assessment_by_id: async (patient_id, assessment_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/assessment/${assessment_id}`),
      "Fetching assessment by ID failed.",
    );
  },

  // Update a test for a patient
  update_assessment: async (patient_id, assessment_id, data) => {
    return apiCall(
      () =>
        api.patch(`/patients/${patient_id}/assessment/${assessment_id}`, data),
      "Updating assessment failed.",
    );
  },

  // Delete a test for a patient
  delete_assessment_by_id: async (patient_id, assessment_id) => {
    return apiCall(
      () => api.delete(`/patients/${patient_id}/assessment/${assessment_id}`),
      "Deleting assessment failed.",
    );
  },

  // ======================
  // Notes
  // ======================
  create_note: async (patient_id, data) => {
    return apiCall(
      () => api.post(`/patients/${patient_id}/notes/`, data),
      "Creating note failed.",
    );
  },

  get_notes_by_patient: async (patient_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/notes/`),
      "Fetching notes by patient failed.",
    );
  },

  get_note_by_id: async (patient_id, note_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/notes/${note_id}`),
      "Fetching note by ID failed.",
    );
  },

  update_note: async (patient_id, note_id, data) => {
    return apiCall(
      () => api.patch(`/patients/${patient_id}/notes/${note_id}`, data),
      "Updating note failed.",
    );
  },

  delete_note_by_id: async (patient_id, note_id) => {
    return apiCall(
      () => api.delete(`/patients/${patient_id}/notes/${note_id}`),
      "Deleting note failed.",
    );
  },

  // ======================
  // Activity
  // ======================
  create_activity: async (patient_id, data) => {
    return apiCall(
      () => api.post(`/patients/${patient_id}/activities/`, data),
      "Creating activity failed.",
    );
  },

  get_activities_by_patient: async (patient_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/activities/`),
      "Fetching activities by patient failed.",
    );
  },

  get_activities: async () => {
    return apiCall(
      () => api.get(`/patients/activities/`),
      "Fetching activities failed.",
    );
  },

  get_activity_by_id: async (patient_id, activity_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/activities/${activity_id}`),
      "Fetching activity by ID failed.",
    );
  },

  update_activity: async (patient_id, activity_id, data) => {
    return apiCall(
      () =>
        api.patch(`/patients/${patient_id}/activities/${activity_id}`, data),
      "Updating activity failed.",
    );
  },

  delete_activity_by_id: async (patient_id, activity_id) => {
    return apiCall(
      () => api.delete(`/patients/${patient_id}/activities/${activity_id}`),
      "Deleting activity failed.",
    );
  },
  // ======================
  // Dispensing
  // ======================
  create_dispensing: async (patient_id, data) => {
    return apiCall(
      () => api.post(`/patients/${patient_id}/dispensings/`, data),
      "Creating dispensing failed.",
    );
  },

  get_dispensings_by_patient: async (patient_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/dispensings/`),
      "Fetching dispensings by patient failed.",
    );
  },

  get_dispensing_by_id: async (patient_id, dispensing_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/dispensings/${dispensing_id}`),
      "Fetching dispensing by ID failed.",
    );
  },

  update_dispensing: async (patient_id, dispensing_id, data) => {
    return apiCall(
      () =>
        api.patch(`/patients/${patient_id}/dispensings/${dispensing_id}`, data),
      "Updating dispensing failed.",
    );
  },

  delete_dispensing_by_id: async (patient_id, dispensing_id) => {
    return apiCall(
      () => api.delete(`/patients/${patient_id}/dispensings/${dispensing_id}`),
      "Deleting dispensing failed.",
    );
  },

  // ======================
  // Medications
  // ======================
  create_medication: async (patient_id, data) => {
    return apiCall(
      () => api.post(`/patients/${patient_id}/medications/`, data),
      "Creating medication failed.",
    );
  },

  get_medications_by_patient: async (patient_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/medications/`),
      "Fetching medications by patient failed.",
    );
  },

  get_medication_by_id: async (patient_id, medication_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/medications/${medication_id}`),
      "Fetching medication by ID failed.",
    );
  },

  update_medication: async (patient_id, medication_id, data) => {
    return apiCall(
      () =>
        api.patch(`/patients/${patient_id}/medications/${medication_id}`, data),
      "Updating medication failed.",
    );
  },

  delete_medication_by_id: async (patient_id, medication_id) => {
    return apiCall(
      () => api.delete(`/patients/${patient_id}/medications/${medication_id}`),
      "Deleting medication failed.",
    );
  },

  // ======================
  // Interactions
  // ======================
  create_interaction: async (patient_id, data) => {
    return apiCall(
      () => api.post(`/patients/${patient_id}/interactions/`, data),
      "Creating interaction failed.",
    );
  },

  get_interactions_by_patient: async (patient_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/interactions/`),
      "Fetching interactions by patient failed.",
    );
  },

  get_interaction_by_id: async (patient_id, interaction_id) => {
    return apiCall(
      () => api.get(`/patients/${patient_id}/interactions/${interaction_id}`),
      "Fetching interaction by ID failed.",
    );
  },

  update_interaction: async (patient_id, interaction_id, data) => {
    return apiCall(
      () =>
        api.patch(
          `/patients/${patient_id}/interactions/${interaction_id}`,
          data,
        ),
      "Updating interaction failed.",
    );
  },

  delete_interaction_by_id: async (patient_id, interaction_id) => {
    return apiCall(
      () =>
        api.delete(`/patients/${patient_id}/interactions/${interaction_id}`),
      "Deleting interaction failed.",
    );
  },
};
