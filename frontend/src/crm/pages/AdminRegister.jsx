import React, { useState, useEffect } from "react";
import Client from "../components/Client";
import Tests from "../components/Tests";
import Intake from "../components/Intake";
import Dispensing from "../components/Dispensing";
import Medications from "../components/Medication";
import Notes from "../components/Notes";
import Activities from "../components/Activities";
import Interactions from "../components/Interactions";
import Attachments from "../components/Attachments";
import ClinicalTemplateManager from "../components/ClinicalTemplateManager";
import DispositionManager from "../components/DispositionManager";
import ReferralSiteManager from "../components/ReferralSiteManager";
import VoiceDataModal from "../components/VoiceDateModal";
import { useAuth } from "../../context/AuthContext";
import {
  calculateAge,
  copyFormData,
  copyLabelsData,
  getFormattedLabelsData,
  parseDateFromSpeech,
} from "../../utils/utils";
import { GeneralServices } from "../../services/generalService";
import { PatientServices } from "../../services/patientServices";
import RegistrationSaved from "../components/RegistrationSaved";
import { DEFAULT_FORM } from "../forms/Registration";

const AdminRegister = () => {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [activeTab, setActiveTab] = useState("client");
  const { userRole, userPermissions } = useAuth();
  const [showVoiceDateModal, setShowVoiceDateModal] = useState(false);
  const [showDispositionManager, setShowDispositionManager] = useState(false);
  const [showReferralSiteManager, setShowReferralSiteManager] = useState(false);
  const [showClinicalTemplateManager, setShowClinicalTemplateManager] =
    useState(false);
  const [templates, setTemplates] = useState({});
  const [availableReferralSites, setAvailableReferralSites] = useState([]);
  const [availableDispositions, setAvailableDispositions] = useState([]);
  const [availableClinicalTemplates, setAvailableClinicalTemplates] = useState(
    [],
  );
  const [selectedTemplate, setSelectedTemplate] = useState("Select");

  const [voiceDateInput, setVoiceDateInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentRegistrationId, setCurrentRegistrationId] = useState(null);
  const [savedTests, setSavedTests] = useState([]);
  const [savedNotes, setSavedNotes] = useState([]);
  const [savedAttachments, setSavedAttachments] = useState([]);
  const [savedMedications, setSavedMedications] = useState([]);
  const [savedDispensing, setSavedDispensing] = useState([]);
  const [savedInteractions, setSavedInteractions] = useState([]);
  const [savedActivities, setSavedActivities] = useState([]);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoUploadStatus, setPhotoUploadStatus] = useState(null);

  const [dispositionSearch, setDispositionSearch] = useState("");

  const getDefaultForm = () => ({
    ...DEFAULT_FORM,
    regDate: new Date().toISOString().split("T")[0],
    hivDate: new Date().toISOString().split("T")[0],
    rnaSample: new Date().toISOString().split("T")[0],
  });

  const [formData, setFormData] = useState(getDefaultForm());

  const handleVoiceDateSubmit = () => {
    const parsedDate = parseDateFromSpeech(voiceDateInput);

    if (parsedDate) {
      setFormData((prev) => {
        const newData = {
          ...prev,
          [currentVoiceDateField]: parsedDate,
        };

        // Calculate age if DOB
        if (currentVoiceDateField === "dob") {
          const age = calculateAge(parsedDate);
          if (age) {
            newData.age = age.toString();
          }
        }

        return newData;
      });

      setShowVoiceDateModal(false);
      setVoiceDateInput("");
    } else {
      alert(
        `❌ Could not understand date: "${voiceDateInput}". Try saying it like "January 15th 2024" or "today"`,
      );
    }
  };

  const getTests = async (registrationId) => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_tests_by_patient(registrationId);

    if (result.success) {
      setSavedTests(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const getAttachments = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_attachments_by_patient(registrationId);

    if (result.success) {
      setSavedAttachments(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const getNotes = async (registrationId) => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_notes_by_patient(registrationId);

    if (result.success) {
      setSavedNotes(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
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
      setSavedMedications(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const getInteractions = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_interactions_by_patient(registrationId);
    if (result.success) {
      setSavedInteractions(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
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
      setSavedDispensing(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
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
      setSavedActivities(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const tabComponents = {
    client: (
      <Client
        formData={formData}
        setShowVoiceDateModal={setShowVoiceDateModal}
        setFormData={setFormData}
        setShowDispositionManager={setShowDispositionManager}
        setShowReferralSiteManager={setShowReferralSiteManager}
        setShowClinicalTemplateManager={setShowClinicalTemplateManager}
        availableDispositions={availableDispositions}
        availableReferralSites={availableReferralSites}
        availableClinicalTemplates={availableClinicalTemplates}
        setTemplates={setTemplates}
        templates={templates}
        selectedTemplate={selectedTemplate}
        setSelectedTemplate={setSelectedTemplate}
      />
    ),
    tests: (
      <Tests
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
        savedTests={savedTests}
        setSavedTests={setSavedTests}
        getTests={getTests}
      />
    ),
    medication: (
      <Medications
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
        setSavedMedications={setSavedMedications}
        savedMedications={savedMedications}
        getMedications={getMedications}
      />
    ),
    dispensing: (
      <Dispensing
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
        setSavedDispensing={setSavedDispensing}
        savedDispensing={savedDispensing}
        getDispensing={getDispensing}
      />
    ),
    notes: (
      <Notes
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
        setSavedNotes={setSavedNotes}
        savedNotes={savedNotes}
        getNotes={getNotes}
      />
    ),
    activities: (
      <Activities
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
        setSavedActivities={setSavedActivities}
        savedActivities={savedActivities}
        getActivities={getActivities}
      />
    ),
    interactions: (
      <Interactions
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
        setSavedInteractions={setSavedInteractions}
        savedInteractions={savedInteractions}
        getInteractions={getInteractions}
      />
    ),
    attachments: (
      <Attachments
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
        setSavedAttachments={setSavedAttachments}
        savedAttachments={savedAttachments}
        getAttachments={getAttachments}
      />
    ),
  };

  // Check if user has permission for a tab
  const hasTabPermission = (tabId) => {
    if (userRole === "admin") return true;

    return Array.isArray(userPermissions) && userPermissions.includes(tabId);
  };

  // Get allowed tabs based on user permissions
  const getAllowedTabs = () => {
    const allTabs = [
      { id: "client", name: "Client" },
      { id: "tests", name: "Tests" },
      { id: "medication", name: "Medication" },
      { id: "dispensing", name: "Dispensing" },
      { id: "notes", name: "Notes" },
      { id: "activities", name: "Activities" },
      { id: "interactions", name: "Interactions" },
      { id: "attachments", name: "Attachments" },
    ];

    return allTabs.filter((tab) => hasTabPermission(tab.id));
  };

  const getDispositions = async (e) => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_dispositions();

    if (result.success) {
      setAvailableDispositions(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const getReferralSites = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_referral_sites();

    if (result.success) {
      setAvailableReferralSites(result.data);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const getClinicalTemplates = async () => {
    setLoading(true);
    setError("");

    const result = await GeneralServices.get_clinical_templates();

    if (result.success) {
      setAvailableClinicalTemplates(result.data);

      const templatesObject = {};
      // Convert array to object for easier access
      result.data.forEach((template) => {
        templatesObject[template.name] = template.content;
      });

      setTemplates(templatesObject);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    getDispositions();
    getReferralSites();
    getClinicalTemplates();
  }, []);

  const resetForm = async () => {
    setFormData(getDefaultForm());
    setPhotoPreview(null);
    setPhotoUploadStatus(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  function validateForm() {
    // Client-side validation for required fields
    if (!formData.first_name.trim()) {
      setSubmitStatus({
        type: "error",
        message: "First Name is required.",
      });
      setIsSubmitting(false);
      return false;
    }

    if (!formData.last_name.trim()) {
      setSubmitStatus({
        type: "error",
        message: "Last Name is required.",
      });
      setIsSubmitting(false);
      return false;
    }

    if (!formData.patient_consent) {
      setSubmitStatus({
        type: "error",
        message: "Patient Consent is required.",
      });
      setIsSubmitting(false);
      return false;
    }

    // Check if photo is too large before sending
    if (formData.photo && formData.photo.length > 1200 * 1024) {
      // Increased from 1MB to 1.2MB
      setSubmitStatus({
        type: "error",
        message:
          "Photo is too large for submission. Please try uploading a different photo.",
      });
      setIsSubmitting(false);
      return false;
    }
    return true;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    // if (!validateForm()) {
    //   return;
    // }

    // Clean the form data - remove empty strings for optional fields and convert to null
    const cleanedFormData = { ...formData };

    // Add selectedTemplate to form data for database storage
    // cleanedFormData.selectedTemplate = selectedTemplate; // Handle clincial template

    // Convert empty strings to null for date fields
    if (cleanedFormData.dob === "") {
      cleanedFormData.dob = null;
    }
    if (cleanedFormData.regDate === "") {
      cleanedFormData.regDate = null;
    }

    // Convert empty strings to null for optional fields
    Object.keys(cleanedFormData).forEach((key) => {
      if (cleanedFormData[key] === "") {
        cleanedFormData[key] = null;
      }
    });

    const result = await PatientServices.create_patient(cleanedFormData);

    if (result.success) {
      const id = result.data?.patient_id;
      if (!id) {
        setLoading(false);
        setIsSubmitting(false);
        return;
      }
      setCurrentRegistrationId(id);

      await getTests(id);
      await getAttachments(id);
      await getNotes(id);
      await getMedications(id);
      await getInteractions(id);
      await getDispensing(id);
      await getActivities(id);

      setSubmitStatus({
        type: "success",
        message:
          "Registration saved for review! You can now access the dashboard to review and finalize registrations.",
        id: id,
      });

      // Trigger dashboard refresh
      localStorage.setItem("new_registration_submitted", Date.now().toString());

      resetForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }

    setLoading(false);
    setIsSubmitting(false);
  };

  const handleCopyLabel = () => {
    copyLabelsData(formData);
  };

  const handleCopy = () => {
    copyFormData(currentRegistrationId, formData);
  };

  if (submitStatus?.type === "success") {
    return (
      <RegistrationSaved
        submitStatus={submitStatus}
        setSubmitStatus={setSubmitStatus}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <form onSubmit={handleSubmit} className="space-y-6">
            <Intake submitStatus={submitStatus} setFormData={setFormData} />

            {/* Tabs Navigation */}
            <div className="border-b border-gray-200 mb-6 relative">
              {getAllowedTabs().length > 0 ? (
                <div className="flex space-x-1 overflow-x-auto scrollbar-hide">
                  {getAllowedTabs().map((tab) => (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() => setActiveTab(tab.id)}
                      className={`px-4 py-2 text-sm font-medium whitespace-nowrap relative ${
                        activeTab === tab.id
                          ? "border-b-2 border-white text-black bg-white -mb-0.5 z-10"
                          : "border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                      }`}
                    >
                      {tab.name}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-500 text-lg mb-2">
                    🔒 Access Restricted
                  </div>
                  <p className="text-gray-600 mb-4">
                    You don't have permission to access any registration tabs.
                  </p>
                  <button
                    onClick={() => navigate("/admin-menu")}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Back to Menu
                  </button>
                </div>
              )}
            </div>

            {/* Tab Content  */}
            <div className="tab-content">
              {tabComponents[activeTab] || null}
            </div>

            {/* Save Button - Only show in Patient tab */}
            {activeTab === "client" && (
              <div className="border-t pt-6 space-y-4">
                {/* Labels Button */}
                <button
                  type="button"
                  onClick={handleCopyLabel}
                  className="w-full bg-black text-white py-3 px-6 rounded-md hover:bg-gray-800 transition-colors text-lg font-semibold"
                >
                  Labels
                </button>
                {/* Copy Button */}
                <button
                  type="button"
                  onClick={handleCopy}
                  className="w-full bg-black text-white py-3 px-6 rounded-md hover:bg-gray-800 transition-colors text-lg font-semibold"
                >
                  Copy
                </button>
                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-black text-white py-3 px-6 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-lg font-semibold"
                >
                  {isSubmitting ? "Saving..." : "Save"}
                </button>
              </div>
            )}
          </form>
        </div>
      </div>

      {showVoiceDateModal && (
        <VoiceDataModal
          setShowVoiceDateModal={setShowVoiceDateModal}
          voiceDateInput={voiceDateInput}
          setVoiceDateInput={setVoiceDateInput}
          handleVoiceDateSubmit={handleVoiceDateSubmit}
        />
      )}
      {showDispositionManager && (
        <DispositionManager
          setShowDispositionManager={setShowDispositionManager}
          availableDispositions={availableDispositions}
          getDispositions={getDispositions}
        />
      )}
      {showReferralSiteManager && (
        <ReferralSiteManager
          setShowReferralSiteManager={setShowReferralSiteManager}
          availableReferralSites={availableReferralSites}
          getReferralSites={getReferralSites}
        />
      )}
      {showClinicalTemplateManager && (
        <ClinicalTemplateManager
          setShowClinicalTemplateManager={setShowClinicalTemplateManager}
          availableClinicalTemplates={availableClinicalTemplates}
          getClinicalTemplates={getClinicalTemplates}
        />
      )}
    </div>
  );
};

export default AdminRegister;
// {isFullScreenPreview && documentPreview && <DocumentPreviewModal />}
