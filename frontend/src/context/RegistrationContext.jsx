import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { GeneralServices } from "../services/generalService";
import { PatientServices } from "../services/patientServices";
import { ObjectServices } from "../services/objectService";

const RegistrationContext = createContext();

export const useRegistration = () => useContext(RegistrationContext);

export function RegistrationProvider({ children }) {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Dashboard
  const [pendingData, setPendingData] = useState([]);
  const [finalizedData, setFinalizedData] = useState([]);
  const [activityData, setActivityData] = useState([]);

  // Generic
  const [referralSites, setReferralSites] = useState([]);
  const [dispositions, setDispositions] = useState([]);
  const [notesTemplates, setNotesTemplates] = useState([]);
  const [clinicalTemplates, setClinicalTemplates] = useState([]);
  const [documentTypes, setDocumentTypes] = useState([]);
  const [medicationTemplates, setMedicationTemplates] = useState([]);
  const [outcomes, setOutcomes] = useState([]);
  const [genericInteractions, setGenericInteractions] = useState([]);
  const [genericCoverage, setGenericCoverage] = useState([]);

  // Patient
  const [registrationId, setRegistrationId] = useState(null);
  const [interactions, setInteractions] = useState([]);
  const [dispensing, setDispensing] = useState([]);
  const [medications, setMedications] = useState([]);
  const [activities, setActivities] = useState([]);
  const [tests, setTests] = useState([]);
  const [notes, setNotes] = useState([]);

  // Modals
  const [showInteractionManager, setShowInteractionManager] = useState(false);
  const [showCoverageManager, setShowCoverageManager] = useState(false);
  const [showNoteManager, setShowNoteManager] = useState(false);
  const [showDocumentTypeManager, setShowDocumentTypeManager] = useState(false);
  const [showDispositionManager, setShowDispositionManager] = useState(false);
  const [showReferralSiteManager, setShowReferralSiteManager] = useState(false);
  const [showClinicalManager, setShowClinicalManager] = useState(false);
  const [showMedicationManager, setShowMedicationManager] = useState(false);
  const [showOutcomeManager, setShowOutcomeManager] = useState(false);

  // -- Dashboard
  // Activities
  const getDashboardActivities = async () => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_activities();

    if (result.success) {
      setActivityData(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }
    setLoading(false);
  };

  // Pending and Finalized
  const getRegistrations = async () => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_patients();

    if (result.success) {
      const pending = result.data.filter((reg) => reg.status === "pending");
      setPendingData(pending);

      const finalized = result.data.filter(
        (reg) => reg.status === "finalized" || reg.status === "saved",
      );
      setFinalizedData(finalized);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }
    setLoading(false);
  };

  // --  Registration
  const getPatient = async () => {
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

  const getInteractions = async (registrationId) => {
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

  const getDispensing = async (registrationId) => {
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

  const getMedications = async (registrationId) => {
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

  const getTests = async (registrationId) => {
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

  const getNotes = async (registrationId) => {
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

  const getActivities = async (registrationId) => {
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

  const getRegistrationData = async (registrationId) => {
    getTests(registrationId);
    getMedications(registrationId);
    getDispensing(registrationId);
    getNotes(registrationId);
    getActivities(registrationId);
    getInteractions(registrationId);
  };

  // -- General Data
  const getDispositions = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_dispositions();

    if (result.success) {
      setDispositions(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  // -- Notes
  const getNoteTemplates = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_note_templates();

    if (result.success) {
      setNotesTemplates(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting note templates.");
      } else {
        setError("Error getting note templates. Please try again.");
      }
    }
    setLoading(false);
  };
  // Referral Sites
  const getReferralSites = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_referral_sites();

    if (result.success) {
      setReferralSites(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting referral sites.");
      } else {
        setError("Error getting referral sites. Please try again.");
      }
    }
    setLoading(false);
  };

  // Referral Sites
  const getMedicationTemplates = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_medication_template();

    if (result.success) {
      setMedicationTemplates(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting medication templates.");
      } else {
        setError("Error getting medication templates. Please try again.");
      }
    }
    setLoading(false);
  };

  // Referral Sites
  const getOutcomes = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_medication_outcomes();

    if (result.success) {
      setOutcomes(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting outcomes.");
      } else {
        setError("Error getting outcomes. Please try again.");
      }
    }
    setLoading(false);
  };

  // Generic interaction
  const getGenericInteractions = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_general_type("interaction");

    if (result.success) {
      setGenericInteractions(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting interactions.");
      } else {
        setError("Error getting interactions. Please try again.");
      }
    }
    setLoading(false);
  };

  const getCoverageTypes = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_general_type("coverage");

    if (result.success) {
      setGenericCoverage(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting outcomes.");
      } else {
        setError("Error getting outcomes. Please try again.");
      }
    }
    setLoading(false);
  };

  // clinical templates
  const getClinicalTemplates = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_clinical_templates();

    if (result.success) {
      setClinicalTemplates(result.data);

      const templatesObject = {};
      // Convert array to object for easier access
      result.data.forEach((template) => {
        templatesObject[template.name] = template.content;
      });

      // setTemplates(templatesObject);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting clinical templates.");
      } else {
        setError("Error getting clinical templates. Please try again.");
      }
    }
    setLoading(false);
  };

  // document types
  const getDocumentTypes = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_document_types();

    if (result.success) {
      setDocumentTypes(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting document types.");
      } else {
        setError("Error getting document types. Please try again.");
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    const getInitialData = async () => {
      getDispositions();
      getClinicalTemplates();
      getDocumentTypes();
      getNoteTemplates();
      getReferralSites();
      getOutcomes();
      getMedicationTemplates();
      getActivities();
      getDashboardActivities();
      getRegistrations();
      getGenericInteractions();
      getCoverageTypes();
    };

    getInitialData();
  }, []);

  return (
    <RegistrationContext.Provider
      value={{
        genericCoverage,
        genericInteractions,
        getGenericInteractions,
        getCoverageTypes,
        medicationTemplates,
        outcomes,
        referralSites,
        dispositions,
        notesTemplates,
        clinicalTemplates,
        documentTypes,
        pendingData,
        finalizedData,
        activityData,
        registrationId,
        interactions,
        dispensing,
        medications,
        tests,
        notes,
        activities,
        getActivities,
        setShowOutcomeManager,
        showOutcomeManager,
        setShowMedicationManager,
        showMedicationManager,
        setShowNoteManager,
        showNoteManager,
        setShowDocumentTypeManager,
        showDocumentTypeManager,
        setShowDispositionManager,
        showDispositionManager,
        setShowReferralSiteManager,
        showReferralSiteManager,
        setShowClinicalManager,
        showClinicalManager,
        getReferralSites,
        getNoteTemplates,
        getDispositions,
        getDocumentTypes,
        getClinicalTemplates,
        getDashboardActivities,
        getRegistrations,
        getPatient,
        getInteractions,
        getDispensing,
        getMedications,
        getMedicationTemplates,
        getTests,
        getNotes,
        getRegistrationData,
        getOutcomes,
        setShowInteractionManager,
        showInteractionManager,
        setShowCoverageManager,
        showCoverageManager,
      }}
    >
      {children}
    </RegistrationContext.Provider>
  );
}
