import { useState, useEffect } from "react";
import Client from "../components/Client";
import Tests from "../tabs/Tests";
import Intake from "../components/Intake";
import Dispensing from "../tabs/Dispensing";
import Medications from "../tabs/Medication";
import Notes from "../tabs/Notes";
import Activities from "../tabs/Activities";
import Interactions from "../tabs/Interactions";
import Attachments from "../tabs/Attachments";
import ClinicalTemplateManager from "../managers/ClinicalTemplateManager";
import DispositionManager from "../managers/DispositionManager";
import ReferralSiteManager from "../managers/ReferralSiteManager";
import VoiceDataModal from "../components/VoiceDateModal";
import { useAuth } from "../../context/AuthContext";
import { calculateAge } from "../../utils/formatData";
import { copyFormData, copyLabelsData } from "../../utils/labelData";
import { parseDateFromSpeech, parseFields } from "../../utils/parseFromSpeech";
import { PatientServices } from "../../services/patientServices";
import RegistrationSaved from "../components/RegistrationSaved";
import { DEFAULT_FORM } from "../forms/Registration";
import VoiceFillModal from "../components/VoiceInput";
import ForceRegisterModal from "../components/ForcePopupModal";
import { ObjectServices } from "../../services/objectService";
import { useRegistration } from "../../context/RegistrationContext";

const AdminRegister = () => {
  const {
    showDispositionManager,
    showReferralSiteManager,
    showClinicalManager,
    getRegistrations,
  } = useRegistration();

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [voiceInputText, setVoiceInputText] = useState("");
  const [submitStatus, setSubmitStatus] = useState(null);
  const [activeTab, setActiveTab] = useState("client");
  const { userRole, userPermissions } = useAuth();
  const [showVoiceDateModal, setShowVoiceDateModal] = useState(false);
  const [showVoiceFillModal, setShowVoiceFillModal] = useState(false);
  const [templates, setTemplates] = useState({});
  const [selectedTemplate, setSelectedTemplate] = useState("Select");
  const [showForceButton, setShowForceButton] = useState(false);
  const [voiceDateInput, setVoiceDateInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentRegistrationId, setCurrentRegistrationId] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoUploadStatus, setPhotoUploadStatus] = useState(null);
  const [currentVoiceDateField, setCurrentVoiceDateField] = useState("");
  const [photoData, setPhotoData] = useState({});

  const getDefaultForm = () => ({
    ...DEFAULT_FORM,
    reg_date: new Date().toISOString().split("T")[0],
    hiv_date: new Date().toISOString().split("T")[0],
    rna_sample_date: new Date().toISOString().split("T")[0],
  });

  const [formData, setFormData] = useState(getDefaultForm());

  const openVoiceDateInput = (dateField) => {
    setCurrentVoiceDateField(dateField);
    setVoiceDateInput("");
    setShowVoiceDateModal(true);
  };

  const openVoiceFillInput = () => {
    setVoiceInputText("");
    setShowVoiceFillModal(true);
  };

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

  const handleVoiceFillSubmit = () => {
    const text = voiceInputText.toLowerCase();
    const parsed = parseFields(text);

    if (parsed) {
      const updatedData = { ...parsed };

      // Calculate age if DOB was parsed
      if (parsed.dob) {
        const calculatedAge = calculateAge(parsed.dob);
        if (calculatedAge !== null) {
          updatedData.age = calculatedAge.toString();
        }
      }

      // Merge into formData
      setFormData((prev) => ({ ...prev, ...updatedData }));

      // Clear voice input & close modal
      setShowVoiceFillModal(false);
      setVoiceInputText("");
    } else {
      alert(
        `❌ Could not understand date: "${voiceDateInput}". Try saying it like "January 15 2024" or "today"`,
      );
    }
  };

  const tabComponents = {
    client: (
      <Client
        formData={formData}
        setShowVoiceDateModal={setShowVoiceDateModal}
        setFormData={setFormData}
        setTemplates={setTemplates}
        templates={templates}
        selectedTemplate={selectedTemplate}
        setSelectedTemplate={setSelectedTemplate}
        openVoiceDateInput={openVoiceDateInput}
        openVoiceFillInput={openVoiceFillInput}
        currentVoiceDateField={currentVoiceDateField}
        setCurrentVoiceDateField={setCurrentVoiceDateField}
      />
    ),
    tests: (
      <Tests
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
      />
    ),
    medication: (
      <Medications
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
      />
    ),
    dispensing: (
      <Dispensing
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
      />
    ),
    notes: (
      <Notes
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
      />
    ),
    activities: (
      <Activities
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
      />
    ),
    interactions: (
      <Interactions
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
      />
    ),
    attachments: (
      <Attachments
        setActiveTab={setActiveTab}
        currentRegistrationId={currentRegistrationId}
      />
    ),
  };

  // Check if user has permission for a tab
  const hasTabPermission = (tabId) => {
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

  const resetForm = async () => {
    setFormData(getDefaultForm());
    setPhotoData({});
    setPhotoPreview(null);
    setPhotoUploadStatus(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  function validateForm() {
    // Client-side validation for required fields
    if (!formData.first_name.trim()) {
      setError("First Name is required.");
      setIsSubmitting(false);
      // 800 seems good for mobile 700 for desktop
      window.scrollTo({ top: 750, behavior: "smooth" });
      return false;
    }

    if (!formData.last_name.trim()) {
      setError("Last Name is required.");
      setIsSubmitting(false);
      window.scrollTo({ top: 750, behavior: "smooth" });
      return false;
    }

    if (!formData.patient_consent) {
      setError("Patient Consent is required.");
      setIsSubmitting(false);
      window.scrollTo({ top: 750, behavior: "smooth" });
      return false;
    }
    if (!formData.dob) {
      setError("Date of birth is required.");
      setIsSubmitting(false);
      window.scrollTo({ top: 750, behavior: "smooth" });
      return false;
    }

    if (!formData.health_card) {
      setError("Health Card Number is required.");
      setIsSubmitting(false);
      window.scrollTo({ top: 750, behavior: "smooth" });
      return false;
    }
    if (formData.health_card.length != 10) {
      setError("Health Card Number must be 10 digits exactly.");
      setIsSubmitting(false);
      window.scrollTo({ top: 750, behavior: "smooth" });
      return false;
    }

    if (!formData.health_card_version) {
      setError("Health Card Version is required.");
      setIsSubmitting(false);
      window.scrollTo({ top: 750, behavior: "smooth" });
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

  const handleForceSubmit = async (e) => {
    const forcedData = { ...formData, force_create: true };
    await handleSubmit(e, forcedData);
  };

  const cancelForceSubmit = async () => {
    setError("");
    setShowForceButton(false);
  };

  const handleSubmit = async (e, dataOverride = formData) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);
    setError("");
    setShowForceButton(false);

    const payload = dataOverride || formData;

    if (!validateForm()) {
      return;
    }

    // Clean the form data - remove empty strings for optional fields and convert to null
    const cleanedFormData = { ...payload };

    // Add selectedTemplate to form data for database storage
    // cleanedFormData.selectedTemplate = selectedTemplate; // Handle clincial template

    // Convert empty strings to null for date fields
    if (cleanedFormData.dob === "") {
      cleanedFormData.dob = null;
    }
    if (cleanedFormData.reg_date === "") {
      cleanedFormData.reg_date = null;
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
      if (photoData.file) {
        const photoRes = await ObjectServices.upload_photo(
          id,
          photoData.name,
          photoData.file,
        );

        if (photoRes.success) {
          setSubmitStatus({
            type: "success",
            message:
              "Registration saved for review! You can now access the dashboard to review and finalize registrations.",
            id: id,
          });

          resetForm();
        } else {
          setError(result.message || "Invalid credentials.");
        }
      } else {
        setSubmitStatus({
          type: "success",
          message:
            "Registration saved for review! You can now access the dashboard to review and finalize registrations.",
          id: id,
        });

        resetForm();
      }
    } else {
      if (result.status === 400 || result.status === 409) {
        if (
          result.message === "Patient with that name and dob already exists."
        ) {
          setShowForceButton(true);
        }
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }
    window.scrollTo({ top: 0, behavior: "smooth" });

    getRegistrations();
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
    window.scrollTo({ top: 0, behavior: "smooth" });
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
            <Intake submitStatus={submitStatus} setPhotoData={setPhotoData} />

            {/* Tabs Navigation */}
            <div id="tabs" className="border-b border-gray-200 mb-6 relative">
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
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded text-sm text-center">
                  {error}
                </div>
              )}
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

      {showVoiceFillModal && (
        <VoiceFillModal
          setShowVoiceFillModal={setShowVoiceFillModal}
          voiceInputText={voiceInputText}
          setVoiceInputText={setVoiceInputText}
          handleVoiceFillSubmit={handleVoiceFillSubmit}
        />
      )}

      {showVoiceDateModal && (
        <VoiceDataModal
          setShowVoiceDateModal={setShowVoiceDateModal}
          voiceDateInput={voiceDateInput}
          setVoiceDateInput={setVoiceDateInput}
          handleVoiceDateSubmit={handleVoiceDateSubmit}
        />
      )}
      {showForceButton && (
        <ForceRegisterModal
          handleForceSubmit={handleForceSubmit}
          cancelForceSubmit={cancelForceSubmit}
          errorMessage={error}
        />
      )}
      {showDispositionManager && <DispositionManager />}
      {showReferralSiteManager && <ReferralSiteManager />}
      {showClinicalManager && <ClinicalTemplateManager />}
    </div>
  );
};

export default AdminRegister;
