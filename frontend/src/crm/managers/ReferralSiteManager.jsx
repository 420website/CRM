import { useState } from "react";
import { GeneralServices } from "../../services/generalService";
import { useRegistration } from "../../context/RegistrationContext";

function EditReferralSiteModal({
  editingReferralSite,
  setShowReferralSiteEditPopup,
  updateReferralSite,
  deleteReferralSite,
}) {
  return (
    <div>
      <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-[60]">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-gray-900">
              Edit Referral Site
            </h3>
            <button
              onClick={() => setShowReferralSiteEditPopup(false)}
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
                Referral Site Name
              </label>
              <input
                type="text"
                id="editReferralSiteName"
                defaultValue={editingReferralSite.name}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="editReferralSiteFrequent"
                defaultChecked={editingReferralSite.is_frequent}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="editReferralSiteFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => {
                  if (editingReferralSite.is_default) {
                    alert("Cannot delete default referral site");
                  } else {
                    deleteReferralSite(
                      editingReferralSite.id,
                      editingReferralSite.name,
                    );
                  }
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  editingReferralSite.is_default
                    ? "bg-gray-400 text-gray-600 cursor-not-allowed"
                    : "bg-black text-white hover:bg-gray-800"
                }`}
                disabled={editingReferralSite.is_default}
              >
                Delete
              </button>
              <button
                type="button"
                onClick={() => setShowReferralSiteEditPopup(false)}
                className="flex-1 py-2 px-4 rounded-md text-sm font-medium bg-black text-white hover:bg-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  const nameInput = document.getElementById(
                    "editReferralSiteName",
                  );
                  const frequentInput = document.getElementById(
                    "editReferralSiteFrequent",
                  );
                  updateReferralSite(
                    editingReferralSite.id,
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

export default function ReferralSiteManager() {
  const { setShowReferralSiteManager, referralSites, getReferralSites } =
    useRegistration();

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [newReferralSiteName, setNewReferralSiteName] = useState("");
  const [editingReferralSite, setEditingReferralSite] = useState(null);
  const [referralSiteSearch, setReferralSiteSearch] = useState("");
  const [newReferralSiteIsFrequent, setNewReferralSiteIsFrequent] =
    useState(false);
  const [showReferralSiteEditPopup, setShowReferralSiteEditPopup] =
    useState(false);

  const createReferralSite = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    if (!newReferralSiteName.trim()) {
      alert("Please enter a referral site name");
      return;
    }

    const data = {
      name: newReferralSiteName.trim(),
      is_frequent: newReferralSiteIsFrequent,
      is_default: false,
    };

    const result = await GeneralServices.create_referral_site(data);

    if (result.success) {
      getReferralSites();
      setMessage("Created referral-site successfully.");
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error creating referral site.");
      } else {
        setError("Error creating referral site. Please try again.");
      }
    }
    setLoading(false);
  };

  const updateReferralSite = async (referralSiteId, name, isFrequent) => {
    setLoading(true);
    setError("");
    setMessage("");

    const data = {
      name: name.trim(),
      is_frequent: isFrequent,
    };

    const result = await GeneralServices.update_referral_site(
      referralSiteId,
      data,
    );

    if (result.success) {
      setEditingReferralSite(null);
      setShowReferralSiteEditPopup(false);
      getReferralSites();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error updating referral site.");
      } else {
        setError("Error updating referral site. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteReferralSite = async (referralSiteId, referralSiteName) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the "${referralSiteName}" referral site?`,
      )
    ) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    const result =
      await GeneralServices.delete_referral_site_by_id(referralSiteId);

    if (result.success) {
      setEditingReferralSite(null);
      setShowReferralSiteEditPopup(false);
      getReferralSites();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error deleting referral site.");
      } else {
        setError("Error deleting referral site. Please try again.");
      }
    }
    setLoading(false);
  };

  const openEditReferralSite = (referralSite) => {
    setEditingReferralSite(referralSite);
    setShowReferralSiteEditPopup(true);
  };

  const closeReferralSiteManager = () => {
    setShowReferralSiteManager(false);
    setNewReferralSiteName("");
    setNewReferralSiteIsFrequent(false);
    setEditingReferralSite(null);
    setShowReferralSiteEditPopup(false);
    setReferralSiteSearch("");
  };

  // Filter referral sites based on search
  const getFilteredReferralSites = () => {
    if (!referralSiteSearch.trim()) {
      return referralSites;
    }

    const searchTerm = referralSiteSearch.toLowerCase();
    return referralSites.filter((site) =>
      site.name.toLowerCase().includes(searchTerm),
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Manage Referral Sites
          </h2>
          <button
            onClick={closeReferralSiteManager}
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
            Search Referral Sites
          </label>
          <input
            type="text"
            value={referralSiteSearch}
            onChange={(e) => setReferralSiteSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Search by referral site name..."
          />
        </div>

        {/* Add New Referral Site Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Add New Referral Site
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
                Referral Site Name
              </label>
              <input
                type="text"
                value={newReferralSiteName}
                onChange={(e) => setNewReferralSiteName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Enter referral site name (e.g., Toronto - Outreach)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newReferralSiteFrequent"
                checked={newReferralSiteIsFrequent}
                onChange={(e) => setNewReferralSiteIsFrequent(e.target.checked)}
                className="w-4 h-4 text-black bg-gray-100 border-gray-300 rounded focus:ring-black"
              />
              <label
                htmlFor="newReferralSiteFrequent"
                className="text-sm text-gray-700"
              >
                Add to "Most Frequently Used" list
              </label>
            </div>
            <button
              type="button"
              onClick={createReferralSite}
              className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Add Referral Site
            </button>
          </div>
        </div>

        {/* Existing Referral Sites List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Existing Referral Sites
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
              {getFilteredReferralSites()
                .filter((s) => s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors"
                    onClick={() => openEditReferralSite(site)}
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
            {getFilteredReferralSites().filter((s) => s.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {referralSiteSearch
                  ? "No frequently used referral sites match your search."
                  : "No frequently used referral sites."}
              </p>
            )}
          </div>

          {/* All Others Section */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2">
              All Others
            </h4>
            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {getFilteredReferralSites()
                .filter((s) => !s.is_frequent)
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((site) => (
                  <div
                    key={site.id}
                    className="p-2 bg-gray-50 border border-gray-200 rounded-md cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => openEditReferralSite(site)}
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
            {getFilteredReferralSites().filter((s) => !s.is_frequent).length ===
              0 && (
              <p className="text-sm text-gray-500 italic">
                {referralSiteSearch
                  ? "No other referral sites match your search."
                  : "No other referral sites."}
              </p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={closeReferralSiteManager}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
      {showReferralSiteEditPopup && editingReferralSite && (
        <EditReferralSiteModal
          editingReferralSite={editingReferralSite}
          setShowReferralSiteEditPopup={setShowReferralSiteEditPopup}
          updateReferralSite={updateReferralSite}
          deleteReferralSite={deleteReferralSite}
        />
      )}
    </div>
  );
}
