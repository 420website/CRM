import { useState } from "react";
import { GeneralServices } from "../../services/generalService";
import { useRegistration } from "../../context/RegistrationContext";

function EditMedicationOutcomeModal({
  editingMedicationOutcome,
  setShowMedicationOutcomeEditPopup,
  updateMedicationOutcome,
  deleteMedicationOutcome,
}) {
  return (
    <div>
      <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-[60]">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-gray-900">Edit Outcome</h3>
            <button
              onClick={() => setShowMedicationOutcomeEditPopup(false)}
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
                Outcome Name
              </label>
              <input
                type="text"
                id="editMedicationOutcomeName"
                defaultValue={editingMedicationOutcome.name}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="editMedicationOutcomeFrequent"
                defaultChecked={editingMedicationOutcome.is_frequent}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="editMedicationOutcomeFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => {
                  if (editingMedicationOutcome.is_default) {
                    alert("Cannot delete default outcome");
                  } else {
                    deleteMedicationOutcome(
                      editingMedicationOutcome.id,
                      editingMedicationOutcome.name,
                    );
                  }
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  editingMedicationOutcome.is_default
                    ? "bg-gray-400 text-gray-600 cursor-not-allowed"
                    : "bg-black text-white hover:bg-gray-800"
                }`}
                disabled={editingMedicationOutcome.is_default}
              >
                Delete
              </button>
              <button
                type="button"
                onClick={() => setShowMedicationOutcomeEditPopup(false)}
                className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  const nameInput = document.getElementById(
                    "editMedicationOutcomeName",
                  );
                  const frequentInput = document.getElementById(
                    "editMedicationOutcomeFrequent",
                  );
                  updateMedicationOutcome(
                    editingMedicationOutcome.id,
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

export default function MedicationOutcomeManager() {
  const { setShowOutcomeManager, outcomes, getOutcomes } = useRegistration();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [newMedicationOutcomeName, setNewMedicationOutcomeName] = useState("");
  const [editingMedicationOutcome, setEditingMedicationOutcome] =
    useState(null);
  const [medicationOutcomeSearch, setMedicationOutcomeSearch] = useState("");
  const [newMedicationOutcomeIsFrequent, setNewMedicationOutcomeIsFrequent] =
    useState(false);
  const [showMedicationOutcomeEditPopup, setShowMedicationOutcomeEditPopup] =
    useState(false);

  const createMedicationOutcome = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newMedicationOutcomeName.trim()) {
      alert("Please enter a outcome name");
      return;
    }

    const data = {
      name: newMedicationOutcomeName.trim(),
      is_frequent: newMedicationOutcomeIsFrequent,
      is_default: false,
    };

    const result = await GeneralServices.create_medication_outcome(data);

    if (result.success) {
      getOutcomes();
      setMessage("Created outcome successfully.");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error creating outcome.");
      } else {
        setError("Error creating outcome. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateMedicationOutcome = async (outcomeId, name, isFrequent) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      is_frequent: isFrequent,
    };

    const result = await GeneralServices.update_medication_outcome(
      outcomeId,
      data,
    );

    if (result.success) {
      setEditingMedicationOutcome(null);
      setShowMedicationOutcomeEditPopup(false);
      getOutcomes();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error updating outcome.");
      } else {
        setError("Error updating outcome. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteMedicationOutcome = async (outcomeId, outcomeName) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the "${outcomeName}" outcome?`,
      )
    ) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    const result =
      await GeneralServices.delete_medication_outcome_by_id(outcomeId);

    if (result.success) {
      setEditingMedicationOutcome(null);
      setShowMedicationOutcomeEditPopup(false);
      getOutcomes();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error deleting outcome.");
      } else {
        setError("Error deleting outcome. Please try again.");
      }
    }
    setLoading(false);
  };

  const openEditMedicationOutcome = (outcome) => {
    setEditingMedicationOutcome(outcome);
    setShowMedicationOutcomeEditPopup(true);
  };

  const closeMedicationOutcomeManager = () => {
    setShowOutcomeManager(false);
    setNewMedicationOutcomeName("");
    setNewMedicationOutcomeIsFrequent(false);
    setEditingMedicationOutcome(null);
    setShowMedicationOutcomeEditPopup(false);
    setMedicationOutcomeSearch("");
  };

  // Filter based on search
  const getFilteredMedicationOutcomes = () => {
    if (!medicationOutcomeSearch.trim()) {
      return outcomes;
    }

    const searchTerm = medicationOutcomeSearch.toLowerCase();
    return outcomes.filter((site) =>
      site.name.toLowerCase().includes(searchTerm),
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Manage Outcomes</h2>
          <button
            onClick={closeMedicationOutcomeManager}
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
            Search Outcomes
          </label>
          <input
            type="text"
            value={medicationOutcomeSearch}
            onChange={(e) => setMedicationOutcomeSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Search by outcome name..."
          />
        </div>

        {/* Add New Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Add New Outcome
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
                Outcome Name
              </label>
              <input
                type="text"
                value={newMedicationOutcomeName}
                onChange={(e) => setNewMedicationOutcomeName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Enter outcome name (e.g., Active)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newMedicationOutcomeFrequent"
                checked={newMedicationOutcomeIsFrequent}
                onChange={(e) =>
                  setNewMedicationOutcomeIsFrequent(e.target.checked)
                }
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="newMedicationOutcomeFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>
            <button
              type="button"
              onClick={createMedicationOutcome}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Add Outcome
            </button>
          </div>
        </div>

        {/* Existing List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Existing Outcomes
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
              {getFilteredMedicationOutcomes()
                .filter((s) => s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                    onClick={() => openEditMedicationOutcome(site)}
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
            {getFilteredMedicationOutcomes().filter((s) => s.is_frequent)
              .length === 0 && (
              <p className="text-sm text-gray-500 italic">
                {medicationOutcomeSearch
                  ? "No frequently used outcome match your search."
                  : "No frequently used outcome."}
              </p>
            )}
          </div>

          {/* All Others Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              All Others
            </h4>
            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {getFilteredMedicationOutcomes()
                .filter((s) => !s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => openEditMedicationOutcome(site)}
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
            {getFilteredMedicationOutcomes().filter((s) => !s.is_frequent)
              .length === 0 && (
              <p className="text-sm text-gray-500 italic">
                {medicationOutcomeSearch
                  ? "No other outcome match your search."
                  : "No other outcome."}
              </p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={closeMedicationOutcomeManager}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
      {showMedicationOutcomeEditPopup && editingMedicationOutcome && (
        <EditMedicationOutcomeModal
          editingMedicationOutcome={editingMedicationOutcome}
          setShowMedicationOutcomeEditPopup={setShowMedicationOutcomeEditPopup}
          updateMedicationOutcome={updateMedicationOutcome}
          deleteMedicationOutcome={deleteMedicationOutcome}
        />
      )}
    </div>
  );
}
