import { useState } from "react";
import { GeneralServices } from "../../services/generalService";
import { useRegistration } from "../../context/RegistrationContext";

function EditMedicationTemplateModal({
  editingMedicationTemplate,
  setShowMedicationTemplateEditPopup,
  updateMedicationTemplate,
  deleteMedicationTemplate,
}) {
  return (
    <div>
      <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-[60]">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-gray-900">
              Edit Medications
            </h3>
            <button
              onClick={() => setShowMedicationTemplateEditPopup(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Medication Name
              </label>
              <input
                type="text"
                id="editMedicationTemplateName"
                defaultValue={editingMedicationTemplate.name}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="editMedicationTemplateFrequent"
                defaultChecked={editingMedicationTemplate.is_frequent}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="editMedicationTemplateFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => {
                  if (editingMedicationTemplate.is_default) {
                    alert("Cannot delete default medication");
                  } else {
                    deleteMedicationTemplate(
                      editingMedicationTemplate.id,
                      editingMedicationTemplate.name,
                    );
                  }
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  editingMedicationTemplate.is_default
                    ? "bg-gray-400 text-gray-600 cursor-not-allowed"
                    : "bg-black text-white hover:bg-gray-800"
                }`}
                disabled={editingMedicationTemplate.is_default}
              >
                Delete
              </button>
              <button
                type="button"
                onClick={() => setShowMedicationTemplateEditPopup(false)}
                className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  const nameInput = document.getElementById(
                    "editMedicationTemplateName",
                  );
                  const frequentInput = document.getElementById(
                    "editMedicationTemplateFrequent",
                  );
                  updateMedicationTemplate(
                    editingMedicationTemplate.id,
                    nameInput.value,
                    frequentInput.checked,
                  );
                }}
                className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function MedicationTemplateManager() {
  const {
    setShowMedicationManager,
    medicationTemplates,
    getMedicationTemplates,
  } = useRegistration();

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [newMedicationTemplateName, setNewMedicationTemplateName] =
    useState("");
  const [editingMedicationTemplate, setEditingMedicationTemplate] =
    useState(null);
  const [medicationTemplatesSearch, setMedicationTemplateSearch] = useState("");
  const [newMedicationTemplateIsFrequent, setNewMedicationTemplateIsFrequent] =
    useState(false);
  const [showMedicationTemplateEditPopup, setShowMedicationTemplateEditPopup] =
    useState(false);

  const createMedicationTemplate = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newMedicationTemplateName.trim()) {
      alert("Please enter a medication name");
      return;
    }

    const data = {
      name: newMedicationTemplateName.trim(),
      is_frequent: newMedicationTemplateIsFrequent,
      is_default: false,
    };

    const result = await GeneralServices.create_medication_template(data);

    if (result.success) {
      getMedicationTemplates();
      setMessage("Created medication successfully.");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error creating medication.");
      } else {
        setError("Error creating medication. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateMedicationTemplate = async (medicationId, name, isFrequent) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      is_frequent: isFrequent,
    };

    const result = await GeneralServices.update_medication_template(
      medicationId,
      data,
    );

    if (result.success) {
      setEditingMedicationTemplate(null);
      setShowMedicationTemplateEditPopup(false);
      getMedicationTemplates();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error updating medication.");
      } else {
        setError("Error updating medication. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteMedicationTemplate = async (medicationId, medicationName) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the "${medicationName}" medication?`,
      )
    ) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    const result =
      await GeneralServices.delete_medication_template_by_id(medicationId);

    if (result.success) {
      setEditingMedicationTemplate(null);
      setShowMedicationTemplateEditPopup(false);
      getMedicationTemplates();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error deleting medication.");
      } else {
        setError("Error deleting medication. Please try again.");
      }
    }
    setLoading(false);
  };

  const openEditMedicationTemplate = (medication) => {
    setEditingMedicationTemplate(medication);
    setShowMedicationTemplateEditPopup(true);
  };

  const closeMedicationTemplateManager = () => {
    setShowMedicationManager(false);
    setNewMedicationTemplateName("");
    setNewMedicationTemplateIsFrequent(false);
    setEditingMedicationTemplate(null);
    setShowMedicationTemplateEditPopup(false);
    setMedicationTemplateSearch("");
  };

  // Filter based on search
  const getFilteredMedicationTemplates = () => {
    if (!medicationTemplatesSearch.trim()) {
      return medicationTemplates;
    }

    const searchTerm = medicationTemplatesSearch.toLowerCase();
    return medicationTemplates.filter((site) =>
      site.name.toLowerCase().includes(searchTerm),
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Manage Medication</h2>
          <button
            onClick={closeMedicationTemplateManager}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Search Section */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Medication
          </label>
          <input
            type="text"
            value={medicationTemplatesSearch}
            onChange={(e) => setMedicationTemplateSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Search by medication name..."
          />
        </div>

        {/* Add New  Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Add New Medication
          </h3>
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          {message && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}

          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Medication Name
              </label>
              <input
                type="text"
                value={newMedicationTemplateName}
                onChange={(e) => setNewMedicationTemplateName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Enter medication name (e.g., Epclusa)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newMedicationTemplateFrequent"
                checked={newMedicationTemplateIsFrequent}
                onChange={(e) =>
                  setNewMedicationTemplateIsFrequent(e.target.checked)
                }
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="newMedicationTemplateFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>
            <button
              type="button"
              onClick={createMedicationTemplate}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Add Medication
            </button>
          </div>
        </div>

        {/* Existing  List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Existing Medication
            <span className="text-sm font-normal text-gray-500 ml-2">
              (Click to edit)
            </span>
          </h3>

          {/* Frequently Used Section */}
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              Most Frequently Used
            </h4>
            <div className="grid grid-cols-3 gap-2">
              {getFilteredMedicationTemplates()
                .filter((s) => s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                    onClick={() => openEditMedicationTemplate(site)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-900 truncate">
                        {site.name}
                      </span>
                      {site.is_default && (
                        <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          D
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
            {getFilteredMedicationTemplates().filter((s) => s.is_frequent)
              .length === 0 && (
              <p className="text-sm text-gray-500 italic">
                {medicationTemplatesSearch
                  ? "No frequently used medication match your search."
                  : "No frequently used medication."}
              </p>
            )}
          </div>

          {/* All Others Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              All Others
            </h4>
            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {getFilteredMedicationTemplates()
                .filter((s) => !s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => openEditMedicationTemplate(site)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-900 truncate">
                        {site.name}
                      </span>
                      {site.is_default && (
                        <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          D
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
            {getFilteredMedicationTemplates().filter((s) => !s.is_frequent)
              .length === 0 && (
              <p className="text-sm text-gray-500 italic">
                {medicationTemplatesSearch
                  ? "No other medication match your search."
                  : "No other medication."}
              </p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={closeMedicationTemplateManager}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
      {showMedicationTemplateEditPopup && editingMedicationTemplate && (
        <EditMedicationTemplateModal
          editingMedicationTemplate={editingMedicationTemplate}
          setShowMedicationTemplateEditPopup={
            setShowMedicationTemplateEditPopup
          }
          updateMedicationTemplate={updateMedicationTemplate}
          deleteMedicationTemplate={deleteMedicationTemplate}
        />
      )}
    </div>
  );
}
