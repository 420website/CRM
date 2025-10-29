import { useState } from "react";
import { GeneralServices } from "../../services/generalService";
import { useRegistration } from "../../context/RegistrationContext";
import EditModal from "./EditModal";

export default function InteractionsManager() {
  const {
    setShowInteractionManager,
    genericInteractions,
    getGenericInteractions,
  } = useRegistration();

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState("");
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [templatesSearch, setTemplateSearch] = useState("");
  const [newTemplateIsFrequent, setNewTemplateIsFrequent] = useState(false);
  const [showTemplateEditPopup, setShowTemplateEditPopup] = useState(false);

  const createTemplate = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newTemplateName.trim()) {
      alert("Please enter a interaction name");
      return;
    }

    const data = {
      name: newTemplateName.trim(),
      is_frequent: newTemplateIsFrequent,
      is_default: false,
    };

    const result = await GeneralServices.create_general("interaction", data);

    if (result.success) {
      getGenericInteractions();
      setMessage("Created interaction successfully.");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error creating interaction.");
      } else {
        setError("Error creating interaction. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateTemplate = async (id, name, isFrequent) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      is_frequent: isFrequent,
    };

    const result = await GeneralServices.update_general(
      "interaction",
      id,
      data,
    );

    if (result.success) {
      setEditingTemplate(null);
      setShowTemplateEditPopup(false);
      getGenericInteractions();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error updating interaction.");
      } else {
        setError("Error updating interaction. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteTemplate = async (id, name) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the "${name}" interaction?`,
      )
    ) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    const result = await GeneralServices.delete_general_by_id(
      "interaction",
      id,
    );

    if (result.success) {
      setEditingTemplate(null);
      setShowTemplateEditPopup(false);
      getGenericInteractions();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error deleting interaction.");
      } else {
        setError("Error deleting interaction. Please try again.");
      }
    }
    setLoading(false);
  };

  const openEditTemplate = (name) => {
    setEditingTemplate(name);
    setShowTemplateEditPopup(true);
  };

  const closeTemplateManager = () => {
    setShowInteractionManager(false);
    setNewTemplateName("");
    setNewTemplateIsFrequent(false);
    setEditingTemplate(null);
    setShowTemplateEditPopup(false);
    setTemplateSearch("");
  };

  // Filter based on search
  const getFilteredTemplates = () => {
    if (!templatesSearch.trim()) {
      return genericInteractions;
    }

    const searchTerm = templatesSearch.toLowerCase();
    return genericInteractions.filter((site) =>
      site.name.toLowerCase().includes(searchTerm),
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Manage Interactions
          </h2>
          <button
            type="button"
            onClick={closeTemplateManager}
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
            Search Interaction
          </label>
          <input
            type="text"
            value={templatesSearch}
            onChange={(e) => setTemplateSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Search by interaction name..."
          />
        </div>

        {/* Add New  Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Add New Interaction
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
                Interaction Name
              </label>
              <input
                type="text"
                value={newTemplateName}
                onChange={(e) => setNewTemplateName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Enter interaction name (e.g., Epclusa)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newTemplateFrequent"
                checked={newTemplateIsFrequent}
                onChange={(e) => setNewTemplateIsFrequent(e.target.checked)}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="newTemplateFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>
            <button
              type="button"
              onClick={createTemplate}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Add Interaction
            </button>
          </div>
        </div>

        {/* Existing  List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Existing Interaction
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
              {getFilteredTemplates()
                .filter((s) => s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                    onClick={() => openEditTemplate(site)}
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
            {getFilteredTemplates().filter((s) => s.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {templatesSearch
                  ? "No frequently used interaction match your search."
                  : "No frequently used interaction."}
              </p>
            )}
          </div>

          {/* All Others Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              All Others
            </h4>
            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {getFilteredTemplates()
                .filter((s) => !s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => openEditTemplate(site)}
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
            {getFilteredTemplates().filter((s) => !s.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {templatesSearch
                  ? "No other interaction match your search."
                  : "No other interaction."}
              </p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={closeTemplateManager}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
      {showTemplateEditPopup && editingTemplate && (
        <EditModal
          name={"Interaction"}
          editingTemplate={editingTemplate}
          setShowTemplateEditPopup={setShowTemplateEditPopup}
          updateTemplate={updateTemplate}
          deleteTemplate={deleteTemplate}
        />
      )}
    </div>
  );
}
