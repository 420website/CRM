import { useState } from "react";
import { GeneralServices } from "../../services/generalService";
import { useRegistration } from "../../context/RegistrationContext";

function EditPopup({
  editingDisposition,
  setShowEditPopup,
  updateDisposition,
  deleteDisposition,
}) {
  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-[60]">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-gray-900">Edit Disposition</h3>
          <button
            onClick={() => setShowEditPopup(false)}
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
              Disposition Name
            </label>
            <input
              type="text"
              id="editDispositionName"
              defaultValue={editingDisposition.name}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="editDispositionFrequent"
              defaultChecked={editingDisposition.is_frequent}
              className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
            />
            <label
              htmlFor="editDispositionFrequent"
              className="text-sm text-gray-700"
            >
              Add to "Most Frequently Used" list
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                if (editingDisposition.is_default) {
                  alert("Cannot delete default disposition");
                } else {
                  deleteDisposition(
                    editingDisposition.id,
                    editingDisposition.name,
                  );
                }
              }}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                editingDisposition.is_default
                  ? "bg-gray-400 text-gray-600 cursor-not-allowed"
                  : "bg-black text-white hover:bg-gray-800"
              }`}
              disabled={editingDisposition.is_default}
            >
              Delete
            </button>
            <button
              type="button"
              onClick={() => setShowEditPopup(false)}
              className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => {
                const nameInput = document.getElementById(
                  "editDispositionName",
                );
                const frequentInput = document.getElementById(
                  "editDispositionFrequent",
                );
                updateDisposition(
                  editingDisposition.id,
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
  );
}

export default function DispositionManager() {
  const { setShowDispositionManager, dispositions, getDispositions } =
    useRegistration();

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [dispositionSearch, setDispositionSearch] = useState("");
  const [newDispositionName, setNewDispositionName] = useState("");
  const [editingDisposition, setEditingDisposition] = useState(null);
  const [showEditPopup, setShowEditPopup] = useState(false);
  const [newDispositionIsFrequent, setNewDispositionIsFrequent] =
    useState(false);

  const createDisposition = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newDispositionName.trim()) {
      alert("Please enter a disposition name");
      return;
    }
    const data = {
      name: newDispositionName.trim(),
      is_frequent: newDispositionIsFrequent,
      is_default: false,
    };

    const result = await GeneralServices.create_disposition(data);
    if (result.success) {
      getDispositions();
      setMessage("Created disposition successfully.");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error creating dispositions.");
      } else {
        setError("Error creating dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateDisposition = async (dispositionId, name, isFrequent) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      is_frequent: isFrequent,
    };

    const result = await GeneralServices.update_disposition(
      dispositionId,
      data,
    );

    if (result.success) {
      setEditingDisposition(null);
      setShowEditPopup(false);
      getDispositions();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error update dispositions.");
      } else {
        setError("Error update dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteDisposition = async (dispositionId, dispositionName) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the "${dispositionName}" disposition?`,
      )
    ) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    const result =
      await GeneralServices.delete_disposition_by_id(dispositionId);

    if (result.success) {
      setEditingDisposition(null);
      setShowEditPopup(false);
      getDispositions();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error deleting dispositions.");
      } else {
        setError("Error deleting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const openEditDisposition = (disposition) => {
    setEditingDisposition(disposition);
    setShowEditPopup(true);
  };

  const closeDispositionManager = () => {
    setShowDispositionManager(false);
    setNewDispositionName("");
    setNewDispositionIsFrequent(false);
    setEditingDisposition(null);
    setShowEditPopup(false);
    setDispositionSearch("");
  };

  // Filter dispositions based on search
  const getFilteredDispositions = () => {
    if (!dispositionSearch.trim()) {
      return dispositions;
    }

    const searchTerm = dispositionSearch.toLowerCase();
    return dispositions.filter((disposition) =>
      disposition.name.toLowerCase().includes(searchTerm),
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Manage Dispositions
          </h2>
          <button
            onClick={closeDispositionManager}
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
            Search Dispositions
          </label>
          <input
            type="text"
            value={dispositionSearch}
            onChange={(e) => setDispositionSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Search by disposition name..."
          />
        </div>

        {/* Add New Disposition Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Add New Disposition
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
                Disposition Name
              </label>
              <input
                type="text"
                value={newDispositionName}
                onChange={(e) => setNewDispositionName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Enter disposition name (e.g., ACTIVE, PENDING)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newDispositionFrequent"
                checked={newDispositionIsFrequent}
                onChange={(e) => setNewDispositionIsFrequent(e.target.checked)}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="newDispositionFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>
            <button
              type="button"
              onClick={createDisposition}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Add Disposition
            </button>
          </div>
        </div>

        {/* Existing Dispositions List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Existing Dispositions
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
              {getFilteredDispositions()
                .filter((d) => d.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((disposition) => (
                  <div
                    key={disposition.id}
                    className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                    onClick={() => openEditDisposition(disposition)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-900 truncate">
                        {disposition.name}
                      </span>
                      {disposition.is_default && (
                        <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          D
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
            {getFilteredDispositions().filter((d) => d.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {dispositionSearch
                  ? "No frequently used dispositions match your search."
                  : "No frequently used dispositions."}
              </p>
            )}
          </div>

          {/* All Others Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              All Others
            </h4>
            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {getFilteredDispositions()
                .filter((d) => !d.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((disposition) => (
                  <div
                    key={disposition.id}
                    className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => openEditDisposition(disposition)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-900 truncate">
                        {disposition.name}
                      </span>
                      {disposition.is_default && (
                        <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          D
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
            {getFilteredDispositions().filter((d) => !d.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {dispositionSearch
                  ? "No other dispositions match your search."
                  : "No other dispositions."}
              </p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={closeDispositionManager}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
      {showEditPopup && editingDisposition && (
        <EditPopup
          editingDisposition={editingDisposition}
          setShowEditPopup={setShowEditPopup}
          updateDisposition={updateDisposition}
          deleteDisposition={deleteDisposition}
        />
      )}
    </div>
  );
}
