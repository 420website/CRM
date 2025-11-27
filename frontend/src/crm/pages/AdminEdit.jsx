import { useState, useEffect, useRef } from "react";
import Client from "../components/Client";
import Dispensing from "../tabs/Dispensing";
import Medications from "../tabs/Medication";
import Notes from "../tabs/Notes";
import Activities from "../tabs/Activities";
import Interactions from "../tabs/Interactions";
import Attachments from "../tabs/Attachments";
import VoiceDataModal from "../components/VoiceDateModal";
import { useAuth } from "../../context/AuthContext";
import { calculateAge, normalizeFormData } from "../../utils/formatData";
import { copyFormData, copyLabelsData } from "../../utils/labelData";
import { parseDateFromSpeech, parseFields } from "../../utils/parseFromSpeech";
import { PatientServices } from "../../services/patientServices";
import EditPhoto from "../components/EditPhoto";
import { useNavigate, useParams } from "react-router-dom";
import { DEFAULT_FORM } from "../forms/Registration";
import VoiceFillModal from "../components/VoiceInput";
import { ObjectServices } from "../../services/objectService";
import { useRegistration } from "../../context/RegistrationContext";
import toast from "react-hot-toast";
import DuplicateModal from "../components/DuplicateModal";
import { useDashboard } from "../../context/DashboardContext";
import Assessments from "../tabs/Assessments";

const AdminEdit = () => {
  const navigate = useNavigate();
  const { registrationId } = useParams();
  const { userRole, userPermissions } = useAuth();
  const { setLastItem } = useDashboard();
  const { getClientAssociatedData } = useRegistration();
  const { getDashboardRegistrations, getDashboardActivities } = useDashboard();
  const hasRun = useRef(false);

  const [voiceInputText, setVoiceInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState("Select");
  const [showVoiceDateModal, setShowVoiceDateModal] = useState(false);
  const [showVoiceFillModal, setShowVoiceFillModal] = useState(false);
  const [currentVoiceDateField, setCurrentVoiceDateField] = useState("");
  const [voiceDateInput, setVoiceDateInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoData, setPhotoData] = useState({});
  const [photoChanged, setPhotoChanged] = useState(false);
  const [templates, setTemplates] = useState({});
  const [showNavigateModal, setShowNavigateModal] = useState(false);
  const [duplicateHealthcardPatient, setDuplicateHealthcardPatient] =
    useState(null);
  const [duplicateIdentity, setDuplicateIdentity] = useState(null);
  const [showNavigateIdentityModal, setShowNavigateIdentityModal] =
    useState(false);
  const [forceSave, setForceSave] = useState(true);

  const getDefaultForm = () => ({
    ...DEFAULT_FORM,
    reg_date: new Date().toISOString().split("T")[0],
    rna_sample_date: new Date().toISOString().split("T")[0],
  });

  // Check if user has permission for a tab
  const hasTabPermission = (tabId) => {
    return Array.isArray(userPermissions) && userPermissions.includes(tabId);
  };

  const getFirstAllowedTab = () => {
    const allTabs = [
      { id: "client", name: "Client" },
      { id: "assessments", name: "Assessments" },
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

    try {
      await getClientPhoto();
      await getClientData();
    } catch (error) {
      toast.error(error);
    }
    setLoading(false);
  };

  const getClientData = async () => {
    const result = await PatientServices.get_patient_by_id(registrationId);

    if (result.success) {
      const merged = { ...DEFAULT_FORM, ...result.data };
      for (const key in merged) {
        if (merged[key] == null) merged[key] = DEFAULT_FORM[key] ?? "";
      }
      setFormData(merged);

      // Load selectedTemplate from database instead of guessing
      if (result.data?.selected_template) {
        setSelectedTemplate(result.data?.selected_template);
      } else {
        setSelectedTemplate("Select");
      }
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Failed to get client data.");
      } else {
        toast.error(result.message || "Failed to get client data.");
      }
    }

    getClientAssociatedData(registrationId);
  };

  const getClientPhoto = async () => {
    const result = await ObjectServices.get_photo_raw(registrationId);

    if (result.success) {
      const blob = new Blob([result.data], { type: "image/jpeg" });
      const url = URL.createObjectURL(blob);
      setPhotoPreview(url);
      setPhotoData({
        name: result.headers["file-name"],
      });
    } else {
      if (result.status === 404) {
        return;
      } else if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Failed to fetch client photo.");
      } else {
        toast.error(result.message || "Failed to fetch client photo.");
      }
    }

    setPhotoChanged(false);
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
    assessments: (
      <Assessments
        setActiveTab={setActiveTab}
        currentRegistrationId={registrationId}
      />
    ),
    medication: (
      <Medications
        setActiveTab={setActiveTab}
        currentRegistrationId={registrationId}
      />
    ),
    dispensing: (
      <Dispensing
        setActiveTab={setActiveTab}
        currentRegistrationId={registrationId}
      />
    ),
    notes: (
      <Notes
        setActiveTab={setActiveTab}
        currentRegistrationId={registrationId}
      />
    ),
    activities: (
      <Activities
        setActiveTab={setActiveTab}
        currentRegistrationId={registrationId}
      />
    ),
    interactions: (
      <Interactions
        setActiveTab={setActiveTab}
        currentRegistrationId={registrationId}
      />
    ),
    attachments: (
      <Attachments
        setActiveTab={setActiveTab}
        currentRegistrationId={registrationId}
        fileId={formData.file_id}
      />
    ),
  };

  // Get allowed tabs based on user permissions
  const getAllowedTabs = () => {
    const allTabs = [
      { id: "client", name: "Client" },
      { id: "assessments", name: "Assessments" },
      { id: "medication", name: "Medication" },
      { id: "dispensing", name: "Dispensing" },
      { id: "notes", name: "Notes" },
      { id: "activities", name: "Activities" },
      { id: "interactions", name: "Interactions" },
      { id: "attachments", name: "Attachments" },
    ];

    return allTabs.filter((tab) => hasTabPermission(tab.id));
  };

  async function validateForm() {
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

    if (formData.health_card && formData.health_card.length != 10) {
      setIsSubmitting(false);
      toast.error("Health Card Number must be 10 digits.");
      document
        .querySelector("#healthcard")
        ?.scrollIntoView({ behavior: "smooth" });
      return false;
    }

    if (formData.health_card && formData.health_card !== "0000000000") {
      if (await checkIfHealthcardExists(formData.health_card)) {
        document
          .querySelector("#healthcard")
          ?.scrollIntoView({ behavior: "smooth" });
        return false;
      }
    }

    return true;
  }

  const handleNavigateToRegistration = (id) => {
    setShowNavigateModal(false);
    setShowNavigateIdentityModal(false);
    navigate(`/admin-edit/${id}`);
  };

  const handleSubmit = async (e, dataOverride = formData) => {
    e.preventDefault();
    setIsSubmitting(true);

    const payload = dataOverride || formData;

    if (!(await validateForm())) {
      setIsSubmitting(false);
      return;
    }

    // Clean the form data - remove empty strings for optional fields and convert to null
    const cleanedFormData = { ...payload };

    // Convert empty strings to null for date fields
    if (cleanedFormData.dob === "") {
      cleanedFormData.dob = null;
    }
    if (cleanedFormData.reg_date === "") {
      cleanedFormData.reg_date = null;
    }
    if (cleanedFormData.address === "") {
      cleanedFormData.province = null;
    }
    if (cleanedFormData.coverage_type === "Select") {
      cleanedFormData.coverage_type = null;
    }
    if (cleanedFormData.selected_template === "") {
      cleanedFormData.rna_result = null;
      cleanedFormData.rna_available = null;
      cleanedFormData.rna_sample_date = null;
      cleanedFormData.selected_template = null;
    }

    cleanedFormData.force_update = forceSave;
    const data = normalizeFormData(cleanedFormData);

    const result = await PatientServices.update_patient(registrationId, data);

    if (result.success) {
      if (photoData.file) {
        const photoRes = await ObjectServices.upload_photo(
          registrationId,
          photoData.name,
          photoData.file,
        );
        if (photoRes.success) {
          setPhotoData({ name: photoData.name });
          setPhotoChanged(false);
          getDashboardRegistrations();
          getDashboardActivities();
          toast.success("Changes saved successfully");
          await getClientData();
        } else {
          toast.error(result.message || "Error updating photo.");
        }
      } else if (!photoPreview && photoChanged) {
        const deleteRes = await ObjectServices.delete_photo(registrationId);
        if (deleteRes.success) {
          getDashboardRegistrations();
          getDashboardActivities();
          toast.success("Changes saved successfully");
          await getClientData();
        } else {
          toast.error(result.message || "Error removing photo.");
        }
      } else {
        getDashboardRegistrations();
        getDashboardActivities();
        toast.success("Changes saved successfully");
        await getClientData();
      }
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Failed editing registration.");
      } else {
        toast.error("Failed editing registration. Please try again.");
      }
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
    setLoading(false);
    setIsSubmitting(false);
    setPhotoChanged(false);
  };

  const checkIfUserExists = async (firstName, lastName, dob) => {
    const data = {
      first_name: firstName,
      last_name: lastName,
      dob: dob,
      id: registrationId,
    };

    const result = await PatientServices.check_identity_exists(data);

    if (result.success) {
      const exists = result.data?.exists;

      if (!exists) {
        return false;
      } else {
        setDuplicateIdentity({
          id: result.data?.user?.id,
          firstName: result.data?.user?.first_name,
          lastName: result.data?.user?.last_name,
        });
        setShowNavigateIdentityModal(true);
        return true;
      }
    }
  };

  const handleContinueDuplicateIdentity = () => {
    setForceSave(true);
    setShowNavigateIdentityModal(null);
  };

  useEffect(() => {
    if (!formData.first_name || !formData.last_name || !formData.dob) return;

    if (!hasRun.current) {
      hasRun.current = true;
      return;
    }

    const timer = setTimeout(() => {
      setForceSave(false);
      checkIfUserExists(formData.first_name, formData.last_name, formData.dob);
    }, 800);

    return () => {
      clearTimeout(timer);
    };
  }, [formData.first_name, formData.last_name, formData.dob]);

  const checkIfHealthcardExists = async (healthCard) => {
    const data = {
      health_card: healthCard,
      id: registrationId,
    };

    const result = await PatientServices.check_healthcard_exists(data);

    if (result.success) {
      const exists = result.data?.exists;

      if (!exists) {
        return false;
      } else {
        setDuplicateHealthcardPatient({
          id: result.data?.user?.id,
          firstName: result.data?.user?.first_name,
          lastName: result.data?.user?.last_name,
        });
        setShowNavigateModal(true);
        return true;
      }
    }
  };

  const handleContinueDuplicateHealthcard = () => {
    setShowNavigateModal(null);
  };

  useEffect(() => {
    if (
      formData.health_card.length != 10 ||
      !formData.health_card ||
      formData.health_card === "0000000000"
    )
      return;

    const timer = setTimeout(() => {
      checkIfHealthcardExists(formData.health_card);
    }, 800);

    return () => {
      clearTimeout(timer);
    };
  }, [formData.health_card]);

  useEffect(() => {
    if (saveStatus?.type === "success") {
      window.scrollTo(0, 0);
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    }
  }, [saveStatus]);

  return (
    <div className="bg-gray-50">
      {showNavigateModal && (
        <DuplicateModal
          title={"Health Card Already Registered"}
          handleGoTo={handleNavigateToRegistration}
          userData={duplicateHealthcardPatient}
          handleContinue={handleContinueDuplicateHealthcard}
        />
      )}
      {showNavigateIdentityModal && (
        <DuplicateModal
          title={"Name and DOB Match Another Registration"}
          handleGoTo={handleNavigateToRegistration}
          userData={duplicateIdentity}
          handleContinue={handleContinueDuplicateIdentity}
        />
      )}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Edit Registration
          </h1>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                setLastItem(null);
                navigate("/admin-menu");
              }}
              className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Admin Menu
            </button>
            <button
              type="button"
              onClick={() => navigate("/admin-dashboard")}
              className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              Back to Dashboard
            </button>
            <button
              type="button"
              onClick={() => navigate("/")}
              className="inline-flex items-center gap-1 px-3 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Home
            </button>
          </div>
        </div>
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
                formData={formData}
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
                          ? "border-b-2 border-white text-black bg-white"
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
                    onClick={() => copyFormData(registrationId, formData)}
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
    </div>
  );
};

export default AdminEdit;
