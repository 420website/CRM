import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import Client from "../components/Client";
import Tests from "../tabs/Tests";
import Intake from "../components/Intake";
import Dispensing from "../tabs/Dispensing";
import Medications from "../tabs/Medication";
import Notes from "../tabs/Notes";
import Activities from "../tabs/Activities";
import Interactions from "../tabs/Interactions";
import Attachments from "../tabs/Attachments";
import VoiceDataModal from "../components/VoiceDateModal";
import VoiceFillModal from "../components/VoiceInput";
import DuplicateModal from "../components/DuplicateModal";
import RegistrationSaved from "../components/RegistrationSaved";
import { PatientServices } from "../../services/patientServices";
import { ObjectServices } from "../../services/objectService";
import { calculateAge, normalizeFormData } from "../../utils/formatData";
import { copyFormData, copyLabelsData } from "../../utils/labelData";
import { parseDateFromSpeech, parseFields } from "../../utils/parseFromSpeech";
import { DEFAULT_FORM } from "../forms/Registration";
import { useAuth } from "../../context/AuthContext";
import { useDashboard } from "../../context/DashboardContext";

const AdminRegister = () => {
  const navigate = useNavigate();
  const { userRole, userPermissions } = useAuth();
  const { getDashboardRegistrations } = useDashboard();

  const [loading, setLoading] = useState(false);
  const [voiceInputText, setVoiceInputText] = useState("");
  const [submitStatus, setSubmitStatus] = useState(null);
  const [activeTab, setActiveTab] = useState("client");
  const [showVoiceDateModal, setShowVoiceDateModal] = useState(false);
  const [showVoiceFillModal, setShowVoiceFillModal] = useState(false);
  const [templates, setTemplates] = useState({});
  const [selectedTemplate, setSelectedTemplate] = useState("Select");
  const [voiceDateInput, setVoiceDateInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentRegistrationId, setCurrentRegistrationId] = useState(null);
  const [currentVoiceDateField, setCurrentVoiceDateField] = useState("");
  const [photoData, setPhotoData] = useState({});
  const [showNavigateModal, setShowNavigateModal] = useState(false);
  const [duplicateHealthcardPatient, setDuplicateHealthcardPatient] =
    useState(null);
  const [duplicateIdentity, setDuplicateIdentity] = useState(null);
  const [forceSave, setForceSave] = useState(false);
  const [showNavigateIdentityModal, setShowNavigateIdentityModal] =
    useState(false);

  const getDefaultForm = () => ({
    ...DEFAULT_FORM,
    reg_date: new Date().toISOString().split("T")[0],
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
        // templates={templates}
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
        fileId={formData.file_id}
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
    window.scrollTo({ top: 0, behavior: "smooth" });
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
      toast.error("Health Card Number must be 10 digits");
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
    setSubmitStatus(null);

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

    cleanedFormData.force_create = forceSave;
    const data = normalizeFormData(cleanedFormData);

    const result = await PatientServices.create_patient(data);

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
          toast.error(photoRes.message || "Invalid credentials.");
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
        toast.error(result.message || "Registration failed.");
      } else {
        toast.error(result.message || "Registration failed. Please try again.");
      }
    }
    window.scrollTo({ top: 0, behavior: "smooth" });

    getDashboardRegistrations();
    setLoading(false);
    setIsSubmitting(false);
  };

  const checkIfUserExists = async (firstName, lastName, dob) => {
    const data = {
      first_name: firstName,
      last_name: lastName,
      dob: dob,
      id: currentRegistrationId,
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
      id: currentRegistrationId,
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
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Intake</h1>
          <div className="flex gap-2">
            <button
              onClick={() => navigate("/admin-menu")}
              className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
              type="button"
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
              onClick={() => navigate("/admin-dashboard")}
              className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
              type="button"
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
              <h1 className="text-gray-500 text-bold text-lg mb-2">
                🔒 Access Restricted
              </h1>
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
              <Intake submitStatus={submitStatus} setPhotoData={setPhotoData} />

              {/* Tabs Navigation */}
              <div
                id="tabs"
                className="border-b border-gray-200 mb-6 relative py-2 scroll-mt-[20px]"
              >
                {getAllowedTabs().length > 0 ? (
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
    </div>
  );
};

export default AdminRegister;
