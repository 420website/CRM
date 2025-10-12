import { useState } from "react";
import { GeneralServices } from "../../services/generalService";

function EditPopup({
  editingDocumentType,
  setShowEditPopup,
  updateDocumentType,
  deleteDocumentType,
}) {
  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-[60]">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-gray-900">
            Edit Document Type
          </h3>
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
              Document Type Name
            </label>
            <input
              type="text"
              id="editDocumentTypeName"
              defaultValue={editingDocumentType.name}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="editDocumentTypeFrequent"
              defaultChecked={editingDocumentType.is_frequent}
              className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
            />
            <label
              htmlFor="editDocumentTypeFrequent"
              className="text-sm text-gray-700"
            >
              Add to "Most Frequently Used" list
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                if (editingDocumentType.is_default) {
                  alert("Cannot delete default document type");
                } else {
                  deleteDocumentType(
                    editingDocumentType.id,
                    editingDocumentType.name,
                  );
                }
              }}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                editingDocumentType.is_default
                  ? "bg-gray-400 text-gray-600 cursor-not-allowed"
                  : "bg-black text-white hover:bg-gray-800"
              }`}
              disabled={editingDocumentType.is_default}
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
                  "editDocumentTypeName",
                );
                const frequentInput = document.getElementById(
                  "editDocumentTypeFrequent",
                );
                updateDocumentType(
                  editingDocumentType.id,
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

export default function DocumentTypeManager({
  setShowDocumentTypeManager,
  availableDocumentTypes,
  getDocumentTypes,
}) {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [documentTypeSearch, setDocumentTypeSearch] = useState("");
  const [newDocumentTypeName, setNewDocumentTypeName] = useState("");
  const [editingDocumentType, setEditingDocumentType] = useState(null);
  const [showEditPopup, setShowEditPopup] = useState(false);
  const [newDocumentTypeIsFrequent, setNewDocumentTypeIsFrequent] =
    useState(false);

  const createDocumentType = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newDocumentTypeName.trim()) {
      alert("Please enter a document type name");
      return;
    }
    const data = {
      name: newDocumentTypeName.trim(),
      is_frequent: newDocumentTypeIsFrequent,
      is_default: false,
    };

    const result = await GeneralServices.create_document_type(data);
    if (result.success) {
      getDocumentTypes();
      setMessage("Created document type successfully.");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error creating document type.");
      } else {
        setError("Error creating document type. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateDocumentType = async (documentTypeId, name, isFrequent) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      is_frequent: isFrequent,
    };

    const result = await GeneralServices.update_document_type(
      documentTypeId,
      data,
    );

    if (result.success) {
      setEditingDocumentType(null);
      setShowEditPopup(false);
      getDocumentTypes();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error update document type.");
      } else {
        setError("Error update document type. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteDocumentType = async (documentTypeId, documentTypeName) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the "${documentTypeName}" document type?`,
      )
    ) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    const result =
      await GeneralServices.delete_document_type_by_id(documentTypeId);

    if (result.success) {
      setEditingDocumentType(null);
      setShowEditPopup(false);
      getDocumentTypes();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error deleting document type.");
      } else {
        setError("Error deleting document type. Please try again.");
      }
    }
    setLoading(false);
  };

  const openEditDocumentType = (documentType) => {
    setEditingDocumentType(documentType);
    setShowEditPopup(true);
  };

  const closeDocumentTypeManager = () => {
    setShowDocumentTypeManager(false);
    setNewDocumentTypeName("");
    setNewDocumentTypeIsFrequent(false);
    setEditingDocumentType(null);
    setShowEditPopup(false);
    setDocumentTypeSearch("");
  };

  // Filter documenttype based on search
  const getFilteredDocumentTypes = () => {
    if (!documentTypeSearch.trim()) {
      return availableDocumentTypes;
    }

    const searchTerm = documentTypeSearch.toLowerCase();
    return availableDocumentTypes.filter((documentType) =>
      documentType.name.toLowerCase().includes(searchTerm),
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Manage Document Types
          </h2>
          <button
            onClick={closeDocumentTypeManager}
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
            Search Document Types
          </label>
          <input
            type="text"
            value={documentTypeSearch}
            onChange={(e) => setDocumentTypeSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Search by document type..."
          />
        </div>

        {/* Add New DocumentType Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Add New Document Type
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
                Document Type Name
              </label>
              <input
                type="text"
                value={newDocumentTypeName}
                onChange={(e) => setNewDocumentTypeName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Enter document type name (e.g., Consultation Report)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newDocumentTypeFrequent"
                checked={newDocumentTypeIsFrequent}
                onChange={(e) => setNewDocumentTypeIsFrequent(e.target.checked)}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="newDocumentTypeFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>
            <button
              type="button"
              onClick={createDocumentType}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Add Document Type
            </button>
          </div>
        </div>

        {/* Existing DocumentTypes List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Existing DocumentTypes
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
              {getFilteredDocumentTypes()
                .filter((d) => d.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((documentType) => (
                  <div
                    key={documentType.id}
                    className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                    onClick={() => openEditDocumentType(documentType)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-900 truncate">
                        {documentType.name}
                      </span>
                      {documentType.is_default && (
                        <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          D
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
            {getFilteredDocumentTypes().filter((d) => d.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {documentTypeSearch
                  ? "No frequently used document types match your search."
                  : "No frequently used document types."}
              </p>
            )}
          </div>

          {/* All Others Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              All Others
            </h4>
            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {getFilteredDocumentTypes()
                .filter((d) => !d.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((documentType) => (
                  <div
                    key={documentType.id}
                    className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => openEditDocumentType(documentType)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-900 truncate">
                        {documentType.name}
                      </span>
                      {documentType.is_default && (
                        <span className="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          D
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
            {getFilteredDocumentTypes().filter((d) => !d.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {documentTypeSearch
                  ? "No other document types match your search."
                  : "No other document types."}
              </p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={closeDocumentTypeManager}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
      {showEditPopup && editingDocumentType && (
        <EditPopup
          editingDocumentType={editingDocumentType}
          setShowEditPopup={setShowEditPopup}
          updateDocumentType={updateDocumentType}
          deleteDocumentType={deleteDocumentType}
        />
      )}
    </div>
  );
}
