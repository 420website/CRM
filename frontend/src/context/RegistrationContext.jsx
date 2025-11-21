import { createContext, useContext, useState } from "react";
import { PatientServices } from "../services/patientServices";
import { ObjectServices } from "../services/objectService";
import { useAuth } from "./AuthContext";

const RegistrationContext = createContext();

export const useRegistration = () => useContext(RegistrationContext);

export function RegistrationProvider({ children }) {
  const { userRole } = useAuth();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Patient
  const [registrationId, setRegistrationId] = useState(null);
  const [tests, setTests] = useState([]);
  const [notes, setNotes] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [dispensing, setDispensing] = useState([]);
  const [medications, setMedications] = useState([]);
  const [activities, setActivities] = useState([]);
  const [attachments, setAttachments] = useState([]);

  // --  Registration
  const getClient = async () => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_patient_by_id(registrationId);

    if (result.success) {
      // Normalize: replace null with default
      const normalized = Object.fromEntries(
        Object.entries(result.data).map(([key, value]) => [
          key,
          value ?? DEFAULT_FORM[key] ?? "",
        ]),
      );

      // Also ensure missing keys are filled from DEFAULT_FORM
      const merged = { ...DEFAULT_FORM, ...normalized };
      setFormData(merged);

      // Load selectedTemplate from database instead of guessing
      if (result.data?.selected_template) {
        setSelectedTemplate(result.data?.selected_template);
      } else {
        setSelectedTemplate("Select");
      }

      const photoRes = await ObjectServices.get_photo_raw(registrationId);

      if (photoRes.success) {
        const blob = new Blob([photoRes.data], { type: "image/jpeg" });
        const url = URL.createObjectURL(blob);
        setPhotoPreview(url);
      }
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }
    setPhotoChanged(false);
    setLoading(false);
  };

  const getClientInteractions = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_interactions_by_patient(registrationId);
    if (result.success) {
      setInteractions(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting interactions.");
      } else {
        setError("Error getting interactions. Please try again.");
      }
    }
    setLoading(false);
  };

  const getClientDispensing = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_dispensings_by_patient(registrationId);
    if (result.success) {
      setDispensing(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispensing.");
      } else {
        setError("Error getting dispensing. Please try again.");
      }
    }
    setLoading(false);
  };

  const getClientMedications = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_medications_by_patient(registrationId);

    if (result.success) {
      setMedications(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting medications.");
      } else {
        setError("Error getting medications. Please try again.");
      }
    }
    setLoading(false);
  };

  const getClientTests = async (registrationId) => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_tests_by_patient(registrationId);

    if (result.success) {
      setTests(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting tests.");
      } else {
        setError("Error getting tests. Please try again.");
      }
    }
    setLoading(false);
  };

  const getClientNotes = async (registrationId) => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_notes_by_patient(registrationId);

    if (result.success) {
      setNotes(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting notes.");
      } else {
        setError("Error getting notes. Please try again.");
      }
    }
    setLoading(false);
  };

  const getClientActivities = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_activities_by_patient(registrationId);
    if (result.success) {
      setActivities(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting activities.");
      } else {
        setError("Error getting activities. Please try again.");
      }
    }
    setLoading(false);
  };

  const getAttachments = async (registrationId) => {
    setLoading(true);

    const result =
      await ObjectServices.get_attachments_by_patient(registrationId);

    if (result.success) {
      setAttachments(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error getting attachments.");
      } else {
        toast.error("Error getting attachments. Please try again.");
      }
    }
    setLoading(false);
  };

  const getClientAssociatedData = async (registrationId) => {
    getClientTests(registrationId);
    getClientMedications(registrationId);
    getClientDispensing(registrationId);
    getClientNotes(registrationId);
    getClientActivities(registrationId);
    getClientInteractions(registrationId);
  };

  return (
    <RegistrationContext.Provider
      value={{
        registrationId,
        interactions,
        dispensing,
        medications,
        tests,
        notes,
        activities,
        getClient,
        getClientActivities,
        getClientInteractions,
        getClientDispensing,
        getClientMedications,
        getClientTests,
        getClientNotes,
        getClientAssociatedData,
      }}
    >
      {children}
    </RegistrationContext.Provider>
  );
}
