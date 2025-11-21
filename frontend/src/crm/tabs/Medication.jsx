import { useState } from "react";
import { PatientServices } from "../../services/patientServices";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import DatePicker from "../ui/DatePicker";
import toast from "react-hot-toast";
import { useAuth } from "../../context/AuthContext";
import { useReferences } from "../../context/ReferenceContext";
import OptionManager from "../managers/OptionManager";

export default function Medications({ setActiveTab, currentRegistrationId }) {
  const { userRole } = useAuth();
  const { medications, getClientMedications } = useRegistration();
  const { setShowManager, showManager, options } = useReferences();

  const [loading, setLoading] = useState(false);
  const [editingMedicationId, setEditingMedicationId] = useState(null);
  const [isSavingMedication, setIsSavingMedication] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteMedicationId, setDeleteMedicationId] = useState(null);
  const [medicationData, setMedicationData] = useState({
    medication: "",
    start_date: "",
    end_date: "",
    outcome: "",
  });

  function validateForm() {
    if (!currentRegistrationId) {
      alert("Please complete the Patient tab first to save medications.");
      setActiveTab("patient");
      return false;
    }

    if (!medicationData.medication || medicationData.medication === "") {
      toast.error("Please select a medication");
      return false;
    }

    if (!medicationData.outcome || medicationData.outcome === "") {
      toast.error("Please select an outcome");
      return false;
    }

    if (medicationData.outcome !== "Tx Pending") {
      if (!medicationData.start_date || medicationData.start_date === "") {
        toast.error("Please select a start date");
        return false;
      }
    }
    return true;
  }

  const saveMedication = async () => {
    if (!validateForm()) {
      return;
    }

    editingMedicationId ? updateMedications() : createMedications();
  };

  const createMedications = async () => {
    setLoading(true);
    setIsSavingMedication(true);

    let data = { ...medicationData };

    if (data.start_date === "") {
      data = { ...data, start_date: null };
    }

    if (data.end_date === "") {
      data = { ...data, end_date: null };
    }

    const result = await PatientServices.create_medication(
      currentRegistrationId,
      data,
    );

    if (result.success) {
      getClientMedications(currentRegistrationId);
      clearMedicationForm();
      toast.success("Medication created successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error creating medications.");
      } else {
        toast.error("Error creating medications. Please try again.");
      }
    }
    setIsSavingMedication(false);
    setLoading(false);
  };

  const updateMedications = async () => {
    setLoading(true);
    setIsSavingMedication(true);

    let data = { ...medicationData };

    if (data.start_date === "") {
      data = { ...data, start_date: null };
    }

    if (data.end_date === "") {
      data = { ...data, end_date: null };
    }
    const result = await PatientServices.update_medication(
      currentRegistrationId,
      editingMedicationId,
      data,
    );

    if (result.success) {
      getClientMedications(currentRegistrationId);
      clearMedicationForm();
      toast.success("Medication updated successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating medication.");
      } else {
        toast.error("Error updating medication. Please try again.");
      }
    }
    setIsSavingMedication(false);
    setLoading(false);
  };

  const deleteMedication = async () => {
    setLoading(true);

    const result = await PatientServices.delete_medication_by_id(
      currentRegistrationId,
      deleteMedicationId,
    );

    if (result.success) {
      getClientMedications(currentRegistrationId);
      toast.success("Medication deleted successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting medication.");
      } else {
        toast.error("Error deleting medication. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleDeleteMedication = async (medicationId) => {
    setDeleteMedicationId(medicationId);
    setShowDeleteConfirm(true);
  };

  // Medication management functions
  const handleMedicationChange = (e) => {
    const { name, value } = e.target;
    setMedicationData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const editMedication = (medication) => {
    setMedicationData({
      medication: medication.medication || "",
      start_date: medication.start_date || "",
      end_date: medication.end_date || "",
      outcome: medication.outcome || "",
    });
    setEditingMedicationId(medication.id);
    // Scroll to top of medication form
    document.querySelector("#tabs")?.scrollIntoView({ behavior: "smooth" });
  };
  const clearMedicationForm = () => {
    setMedicationData({
      medication: "",
      start_date: "",
      end_date: "",
      outcome: "",
    });
    setEditingMedicationId(null);
  };

  return (
    <div>
      <div className="space-y-6">
        {(showManager === "medication" ||
          showManager === "medication_outcome") && (
          <OptionManager type={showManager} />
        )}
        {/* Registration ID Check */}
        {!currentRegistrationId && (
          <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-orange-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-orange-800">
                  Client Registration Required
                </h3>
                <div className="mt-2 text-sm text-orange-700">
                  <p>
                    Please complete and save the Client tab form first before
                    adding tests. This will create a registration record that
                    tests can be associated with.
                  </p>
                </div>
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={() => setActiveTab("client")}
                    className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                  >
                    Go to Client Tab
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        {showDeleteConfirm && (
          <ConfirmModal
            message={"Confirm delete medication"}
            subMessage={"This action cannot be undone"}
            confirm={deleteMedication}
            setShowConfirm={setShowDeleteConfirm}
          />
        )}
        {/* Medication Form */}
        <div
          className={
            !currentRegistrationId ? "opacity-50 pointer-events-none" : ""
          }
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            {editingMedicationId ? "Edit Medication" : "Add Medication"}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="medication"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Medication *
                </label>
                {userRole == "admin" && (
                  <button
                    type="button"
                    onClick={() => setShowManager("medication")}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Manage Medications
                  </button>
                )}
              </div>
              <select
                id="medication"
                name="medication"
                value={medicationData.medication}
                onChange={handleMedicationChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="">Select</option>
                {/* Most Frequently Used */}
                {options["medication"]
                  .filter((d) => d.is_frequent)
                  .map((medication) => (
                    <option key={medication.id} value={medication.name}>
                      {medication.name}
                    </option>
                  ))}
                {/* Separator */}
                {options["medication"].filter((d) => !d.is_frequent).length >
                  0 && <option disabled>-------</option>}
                {/* All Others in Alphabetical Order */}
                {options["medication"]
                  .filter((d) => !d.is_frequent)
                  .sort((a, b) => a.name.localeCompare(b.name))
                  .map((medication) => (
                    <option key={medication.id} value={medication.name}>
                      {medication.name}
                    </option>
                  ))}
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="outcome"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Outcome *
                </label>
                {userRole == "admin" && (
                  <button
                    type="button"
                    onClick={() => setShowManager("medication_outcome")}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Manage Outcomes
                  </button>
                )}
              </div>
              <select
                id="outcome"
                name="outcome"
                value={medicationData.outcome}
                onChange={handleMedicationChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="">Select</option>
                {/* Most Frequently Used */}
                {options["medication_outcome"]
                  .filter((d) => d.is_frequent)
                  .map((outcome) => (
                    <option key={outcome.id} value={outcome.name}>
                      {outcome.name}
                    </option>
                  ))}
                {/* Separator */}
                {options["medication_outcome"].filter((d) => !d.is_frequent)
                  .length > 0 && <option disabled>-------</option>}
                {/* All Others in Alphabetical Order */}
                {options["medication_outcome"]
                  .filter((d) => !d.is_frequent)
                  .sort((a, b) => a.name.localeCompare(b.name))
                  .map((outcome) => (
                    <option key={outcome.id} value={outcome.name}>
                      {outcome.name}
                    </option>
                  ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="start_date"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Start Date
                </label>
                <DatePicker
                  name="start_date"
                  value={medicationData.start_date}
                  onChange={handleMedicationChange}
                  className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="mm/dd/yyyy"
                />
              </div>

              <div>
                <label
                  htmlFor="end_date"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  End Date
                </label>
                <DatePicker
                  name="end_date"
                  value={medicationData.end_date}
                  onChange={handleMedicationChange}
                  className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="mm/dd/yyyy"
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="mt-6 grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={saveMedication}
              disabled={isSavingMedication}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              {isSavingMedication
                ? "Saving..."
                : editingMedicationId
                  ? "Update Medication"
                  : "Save Medication"}
            </button>

            <button
              type="button"
              onClick={clearMedicationForm}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
            >
              Clear Form
            </button>
          </div>
        </div>
        {/* Saved Medications */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Saved Medications
          </h3>

          {medications.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No medications have been saved yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {medications.map((medication, index) => (
                <div
                  key={medication.id}
                  className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg font-semibold text-gray-900">
                          {medication.medication}
                        </span>
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${
                            medication.outcome === "Active"
                              ? "bg-blue-100 text-blue-700"
                              : medication.outcome === "Completed"
                                ? "bg-green-100 text-green-700"
                                : medication.outcome === "Non Compliance"
                                  ? "bg-yellow-100 text-yellow-700"
                                  : medication.outcome === "Side Effect"
                                    ? "bg-red-100 text-red-700"
                                    : medication.outcome === "Did not start"
                                      ? "bg-gray-100 text-gray-700"
                                      : medication.outcome === "Death"
                                        ? "bg-black text-white"
                                        : "bg-gray-100 text-gray-700"
                          }`}
                        >
                          {medication.outcome}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700 space-y-1">
                        {medication.start_date && (
                          <p>
                            <strong>Start Date:</strong> {medication.start_date}
                          </p>
                        )}
                        {medication.end_date && (
                          <p>
                            <strong>End Date:</strong> {medication.end_date}
                          </p>
                        )}
                        {medication.start_date && medication.end_date && (
                          <p>
                            <strong>Duration:</strong>{" "}
                            {Math.ceil(
                              (new Date(medication.end_date) -
                                new Date(medication.start_date)) /
                                (1000 * 60 * 60 * 24),
                            )}{" "}
                            days
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => editMedication(medication)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                        title="Edit medication"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteMedication(medication.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                        title="Delete medication"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
