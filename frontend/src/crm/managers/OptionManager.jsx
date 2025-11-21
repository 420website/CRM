import { useState } from "react";
import EditModal from "./EditModal";
import { useReferences } from "../../context/ReferenceContext";
import { ReferenceServices } from "../../services/referenceService";

export default function OptionManager({ type }) {
  const { options, setShowManager, getOption } = useReferences();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [newOptionName, setNewOptionName] = useState("");
  const [editingOption, setEditingOption] = useState(null);
  const [optionsSearch, setOptionSearch] = useState("");
  const [newOptionIsFrequent, setNewOptionIsFrequent] = useState(false);
  const [showOptionEditPopup, setShowOptionEditPopup] = useState(false);

  const createOption = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newOptionName.trim()) {
      alert("Please enter a option name");
      return;
    }

    const data = {
      name: newOptionName.trim(),
      is_frequent: newOptionIsFrequent,
      is_default: false,
    };

    const result = await ReferenceServices.create_option(type, data);

    if (result.success) {
      getOption(type);
      setMessage(`Created option successfully.`);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || `Error creating option.`);
      } else {
        setError(result.message || `Error creating option. Please try again.`);
      }
    }
    setLoading(false);
  };

  const updateOption = async (id, name, isFrequent) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      is_frequent: isFrequent,
    };

    const result = await ReferenceServices.update_option(type, id, data);

    if (result.success) {
      setEditingOption(null);
      setShowOptionEditPopup(false);
      getOption(type);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || `Error creating ${type} option.`);
      } else {
        setError(
          result.message || `Error creating ${type} option. Please try again.`,
        );
      }
    }
    setLoading(false);
  };

  const deleteOption = async (id, name) => {
    if (
      !window.confirm(`Are you sure you want to delete the "${name}" option?`)
    ) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    const result = await ReferenceServices.delete_option_by_id(type, id);

    if (result.success) {
      setEditingOption(null);
      setShowOptionEditPopup(false);
      getOption(type);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || `Error creating ${type} option.`);
      } else {
        setError(
          result.message || `Error creating ${type} option. Please try again.`,
        );
      }
    }
    setLoading(false);
  };

  const openEditOption = (name) => {
    setEditingOption(name);
    setShowOptionEditPopup(true);
  };

  const closeOptionManager = () => {
    // setShowCoverageManager(false);
    setShowManager("");
    setNewOptionName("");
    setNewOptionIsFrequent(false);
    setEditingOption(null);
    setShowOptionEditPopup(false);
    setOptionSearch("");
  };

  // Filter based on search
  const getFilteredOptions = () => {
    if (!optionsSearch.trim()) {
      return options[type];
    }

    const searchTerm = optionsSearch.toLowerCase();
    return options[type].filter((site) =>
      site.name.toLowerCase().includes(searchTerm),
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Manage Options</h2>
          <button
            type="button"
            onClick={closeOptionManager}
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
            Search Option
          </label>
          <input
            type="text"
            value={optionsSearch}
            onChange={(e) => setOptionSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Search by name..."
          />
        </div>

        {/* Add New  Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Add New Option
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
                Option Name
              </label>
              <input
                type="text"
                value={newOptionName}
                onChange={(e) => setNewOptionName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Enter name (e.g. OW)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newOptionFrequent"
                checked={newOptionIsFrequent}
                onChange={(e) => setNewOptionIsFrequent(e.target.checked)}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="newOptionFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>
            <button
              type="button"
              onClick={createOption}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Add Option
            </button>
          </div>
        </div>

        {/* Existing  List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Existing Options
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
              {getFilteredOptions()
                .filter((s) => s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                    onClick={() => openEditOption(site)}
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
            {getFilteredOptions().filter((s) => s.is_frequent).length === 0 && (
              <p className="text-sm text-gray-500 italic">
                {optionsSearch
                  ? "No frequently used coverage match your search."
                  : "No frequently used coverage."}
              </p>
            )}
          </div>

          {/* All Others Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              All Others
            </h4>
            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {getFilteredOptions()
                .filter((s) => !s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => openEditOption(site)}
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
            {getFilteredOptions().filter((s) => !s.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {optionsSearch
                  ? "No other coverage match your search."
                  : "No other coverage."}
              </p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={closeOptionManager}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
      {showOptionEditPopup && editingOption && (
        <EditModal
          name={type}
          editingTemplate={editingOption}
          setShowTemplateEditPopup={setShowOptionEditPopup}
          updateTemplate={updateOption}
          deleteTemplate={deleteOption}
        />
      )}
    </div>
  );
}
