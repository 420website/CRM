import { useState, useEffect } from "react";
import Client from "../components/Client";
import Tests from "../tabs/Tests";
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
import EditPhoto from "../components/EditPhoto";
import { useNavigate, useParams } from "react-router-dom";
import { DEFAULT_FORM } from "../forms/Registration";
import VoiceFillModal from "../components/VoiceInput";
import ForceRegisterModal from "../components/ForcePopupModal";
import { ObjectServices } from "../../services/objectService";
import DocumentTypeManager from "../managers/DocumentTypeManager";
import { useRegistration } from "../../context/RegistrationContext";
import toast from "react-hot-toast";

const AdminEdit = () => {
  const navigate = useNavigate();
  const {
    showDispositionManager,
    showReferralSiteManager,
    showClinicalManager,
    showDocumentTypeManager,
    getRegistrationData,
  } = useRegistration();
  const { registrationId } = useParams();
  const [voiceInputText, setVoiceInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState("Select");
  const { userRole, userPermissions } = useAuth();
  const [showVoiceDateModal, setShowVoiceDateModal] = useState(false);
  const [showVoiceFillModal, setShowVoiceFillModal] = useState(false);
  const [currentVoiceDateField, setCurrentVoiceDateField] = useState("");
  const [voiceDateInput, setVoiceDateInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentRegistrationId, setCurrentRegistrationId] =
    useState(registrationId);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoUploadStatus, setPhotoUploadStatus] = useState(null);
  const [showForceButton, setShowForceButton] = useState(false);
  const [photoData, setPhotoData] = useState({});
  const [photoChanged, setPhotoChanged] = useState(false);
  const [templates, setTemplates] = useState({});

  const getDefaultForm = () => ({
    ...DEFAULT_FORM,
    reg_date: new Date().toISOString().split("T")[0],
    hiv_date: new Date().toISOString().split("T")[0],
    rna_sample_date: new Date().toISOString().split("T")[0],
  });

  // Check if user has permission for a tab
  const hasTabPermission = (tabId) => {
    return Array.isArray(userPermissions) && userPermissions.includes(tabId);
  };

  const getFirstAllowedTab = () => {
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
    return allTabs.find((tab) => hasTabPermission(tab.id))?.id || "client";
  };

  const [activeTab, setActiveTab] = useState(getFirstAllowedTab());
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

  const getRegistration = async () => {
    setLoading(true);

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
        setPhotoData({
          name: photoRes.headers["file-name"],
        });
      }
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Invalid credentials.");
      } else {
        toast.error("Login failed. Please try again.");
      }
    }

    getRegistrationData(registrationId);
    setPhotoChanged(false);
    setLoading(false);
  };

  useEffect(() => {
    if (registrationId) {
      getRegistration();
    }
  }, [registrationId]);

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
    setPhotoPreview(null);
    setPhotoUploadStatus(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  function validateForm() {
    if (formData.photo && formData.photo.length > 1200 * 1024) {
      toast.error(
        "Photo is too large for submission. Please try uploading a different photo.",
      );
      setIsSubmitting(false);
      return false;
    }

    if (!formData.reg_date) {
      setIsSubmitting(false);
      toast.error("Registration date required");
      document
        .querySelector("#regDate")
        ?.scrollIntoView({ behavior: "smooth" });

      return false;
    }

    if (!formData.first_name.trim()) {
      setIsSubmitting(false);
      toast.error("First Name required");
      document
        .querySelector("#firstName")
        ?.scrollIntoView({ behavior: "smooth" });

      return false;
    }

    if (!formData.last_name.trim()) {
      setIsSubmitting(false);
      toast.error("Last Name required");
      document
        .querySelector("#lastName")
        ?.scrollIntoView({ behavior: "smooth" });
      return false;
    }

    if (!formData.dob) {
      setIsSubmitting(false);
      toast.error("Date of birth required");
      document
        .querySelector("#dateOfBirth")
        ?.scrollIntoView({ behavior: "smooth" });
      return false;
    }

    if (!formData.health_card) {
      setIsSubmitting(false);
      toast.error("Health Card Number required.");
      document
        .querySelector("#healthcard")
        ?.scrollIntoView({ behavior: "smooth" });
      return false;
    }
    if (formData.health_card.length != 10) {
      setIsSubmitting(false);
      toast.error("Health Card Number must be 10 digits.");
      document
        .querySelector("#healthcard")
        ?.scrollIntoView({ behavior: "smooth" });
      return false;
    }

    return true;
  }

  const handleForceSubmit = async (e) => {
    const forcedData = { ...formData, force_update: true };
    await handleSubmit(e, forcedData);
  };

  const cancelForceSubmit = async () => {
    setShowForceButton(false);
  };

  const handleSubmit = async (e, dataOverride = formData) => {
    e.preventDefault();
    setIsSubmitting(true);
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

    const result = await PatientServices.update_patient(
      registrationId,
      cleanedFormData,
    );

    if (result.success) {
      if (photoData.file) {
        const photoRes = await ObjectServices.upload_photo(
          registrationId,
          photoData.name,
          photoData.file,
        );
        if (photoRes.success) {
          toast.success("Changes saved successfully");
        } else {
          toast.error(result.message || "Error updating photo.");
        }
      } else if (!photoPreview && photoChanged) {
        const deleteRes = await ObjectServices.delete_photo(registrationId);
        if (deleteRes.success) {
          toast.success("Changes saved successfully");
        } else {
          toast.error(result.message || "Error removing photo.");
        }
      } else {
        toast.success("Changes saved successfully");
      }
    } else {
      if (result.status === 400 || result.status === 409) {
        if (
          result.message === "Patient with that name and dob already exists."
        ) {
          setShowForceButton(true);
        }
        toast.error(result.message || "Invalid credentials.");
      } else {
        toast.error("Failed. Please try again.");
      }
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
    setLoading(false);
    setIsSubmitting(false);
    setPhotoChanged(false);
  };

  useEffect(() => {
    if (saveStatus?.type === "success") {
      window.scrollTo(0, 0);
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    }
  }, [saveStatus]);

  return (
    <div className="bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          {getAllowedTabs().length == 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-500 text-lg mb-2">
                🔒 Access Restricted
              </div>
              <p className="text-gray-600 mb-4">
                You don't have permission to access any registration tabs.
              </p>
              <button
                type="button"
                onClick={() => navigate("/admin-menu")}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Back to Menu
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <EditPhoto
                saveStatus={saveStatus}
                photoData={photoData}
                setPhotoData={setPhotoData}
                photoPreview={photoPreview}
                setPhotoPreview={setPhotoPreview}
                setPhotoChanged={setPhotoChanged}
              />

              {/* Tabs Navigation */}
              <div
                id="tabs"
                className="border-b border-gray-200 mb-6 relative py-2"
              >
                <div className="flex space-x-1 overflow-x-auto overflow-y-hidden scrollbar-hide">
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
                    onClick={() => copyLabelsData(formData)}
                    className="w-full bg-black text-white py-3 px-6 rounded-md hover:bg-gray-800 transition-colors text-lg font-semibold"
                  >
                    Labels
                  </button>
                  {/* Copy Button */}
                  <button
                    type="button"
                    onClick={() =>
                      copyFormData(currentRegistrationId, formData)
                    }
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
          )}
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
        />
      )}
      {showDispositionManager && <DispositionManager />}
      {showReferralSiteManager && <ReferralSiteManager />}
      {showClinicalManager && <ClinicalTemplateManager />}
      {showDocumentTypeManager && <DocumentTypeManager />}
    </div>
  );
};

export default AdminEdit;
