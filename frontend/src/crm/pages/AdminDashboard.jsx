import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { PatientServices } from "../../services/patientServices";
import PaginationControls from "../ui/PaginationControls";
import { RegistrationItems } from "../ui/RegistrationItem";
import { ActivityItems } from "../ui/ActivityItem";
import { useAuth } from "../../context/AuthContext";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import toast from "react-hot-toast";
import DatePicker from "../ui/DatePicker";

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const {
    referralSites,
    dispositions,
    pendingData,
    finalizedData,
    activityData,
    getRegistrations,
    getDashboardActivities,
  } = useRegistration();

  // Core state
  const [activeTab, setActiveTab] = useState("activities");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  // Search and filter state
  const [searchName, setSearchName] = useState("");
  const [searchDate, setSearchDate] = useState("");
  const [searchDisposition, setSearchDisposition] = useState("");
  const [searchReferralSite, setSearchReferralSite] = useState("");
  const [activitySearchTerm, setActivitySearchTerm] = useState("");
  const [activityStatusFilter, setActivityStatusFilter] = useState("all");

  // Action states
  const [finalizingId, setFinalizingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [revertingId, setRevertingId] = useState(null);

  // Confirmation
  const [deleteRegistrationId, setDeleteRegistrationId] = useState(null);
  const [finalizeRegistrationId, setFinalizeRegistrationId] = useState(null);
  const [revertRegistrationId, setRevertRegistrationId] = useState(null);
  const [saveRegistrationId, setSaveRegistrationId] = useState(null);

  const [showConfirm, setShowConfirm] = useState("");

  // Data state - now paginated
  const [currentData, setCurrentData] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    pending_registrations: 0,
    submitted_registrations: 0,
    total_activities: 0,
  });

  const handleLogout = async () => {
    try {
      logout();
    } catch (error) {
      setError("Logout error:", error);
    }
  };

  const setDisplayed = () => {
    if (activeTab === "activities") {
      setCurrentData(activityData);
    } else if (activeTab === "pending") {
      setCurrentData(pendingData);
    } else {
      setCurrentData(finalizedData);
    }
  };

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    setDashboardStats({
      pending_registrations: pendingData.length,
      submitted_registrations: finalizedData.length,
      total_activities: activityData.length,
    });
    setDisplayed();
  }, [activityData, pendingData, finalizedData]);

  useEffect(() => {
    setCurrentPage(1);
    setDisplayed();
  }, [activeTab]);

  // Handle search changes with debouncing
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      setCurrentPage(1); // Reset to first page when searching
    }, 300); // 300ms debounce

    return () => clearTimeout(debounceTimer);
  }, [
    searchName,
    searchDate,
    searchDisposition,
    searchReferralSite,
    activitySearchTerm,
    activityStatusFilter,
  ]);

  // Handle page changes with scroll to top
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages && !loading) {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handle_refresh = async () => {
    getDashboardActivities();
    getRegistrations();
  };

  // Optimized search handlers
  const handleNameSearch = (value) => {
    setSearchName(value);
  };

  const handleDateSearch = (value) => {
    setSearchDate(value);
  };

  const handleDispositionSearch = (value) => {
    setSearchDisposition(value);
  };

  const handleReferralSiteSearch = (value) => {
    setSearchReferralSite(value);
  };

  const clearAllFilters = () => {
    setSearchName("");
    setSearchDate("");
    setSearchDisposition("");
    setSearchReferralSite("");
    setActivitySearchTerm("");
    setActivityStatusFilter("all");
  };

  const deleteRegistration = async () => {
    const result =
      await PatientServices.delete_patient_by_id(deleteRegistrationId);

    if (result.success) {
      getDashboardActivities();
      getRegistrations();
      toast.success("Registration deleted successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting patient.");
      } else {
        toast.error("Error deleting patient. Please try again.");
      }
    }
  };

  const handleDelete = async (id) => {
    setDeleteRegistrationId(id);
    setShowConfirm("delete");
  };

  const finalizeRegistration = async () => {
    setError(null);

    const result = await PatientServices.update_patient_status(
      finalizeRegistrationId,
      {
        status: "finalized",
      },
    );

    if (result.success) {
      getDashboardActivities();
      getRegistrations();
      toast.success("Registration finalized successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating patient status.");
      } else {
        toast.error("Error updating patient status. Please try again.");
      }
    }
  };

  const handleFinalize = async (id) => {
    setFinalizeRegistrationId(id);
    setShowConfirm("finalize");
  };

  const saveRegistration = async () => {
    setError(null);

    const result = await PatientServices.update_patient_status(
      saveRegistrationId,
      {
        status: "saved",
      },
    );

    if (result.success) {
      getDashboardActivities();
      getRegistrations();
      toast.success("Registration saved successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating patient status.");
      } else {
        toast.error("Error updating patient status. Please try again.");
      }
    }
  };

  const handleSave = async (id) => {
    setSaveRegistrationId(id);
    setShowConfirm("save");
  };

  const revertToPending = async () => {
    setError(null);

    const result = await PatientServices.update_patient_status(
      revertRegistrationId,
      {
        status: "pending",
      },
    );

    if (result.success) {
      getDashboardActivities();
      getRegistrations();
      toast.success("Registration reverted to pending");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating patient status.");
      } else {
        toast.error("Error updating patient status. Please try again.");
      }
    }
  };

  const handleRevertToPending = async (id) => {
    setRevertRegistrationId(id);
    setShowConfirm("revert");
  };

  // Compute filtered data based on active tab + filters
  const getFilteredData = () => {
    let data = [];

    if (activeTab === "activities") {
      data = activityData;
      if (activitySearchTerm) {
        const terms = activitySearchTerm.toLowerCase().trim().split(/\s+/);

        data = data.filter((item) => {
          const haystack =
            `${item.first_name ?? ""} ${item.last_name ?? ""} ${item.description ?? ""}`.toLowerCase();
          return terms.every((term) => haystack.includes(term));
        });
      }

      if (searchDate) {
        data = data.filter((item) => item.date === searchDate);
      }

      if (searchDisposition) {
        data = data.filter(
          (item) =>
            (item.disposition || "").toLowerCase() ===
            searchDisposition.toLowerCase(),
        );
      }

      if (searchReferralSite) {
        data = data.filter(
          (item) =>
            (item.referral_site || "").toLowerCase() ===
            searchReferralSite.toLowerCase(),
        );
      }

      if (activityStatusFilter === "completed") {
        data = data.filter((item) => item.completed === true);
      } else if (
        activityStatusFilter === "late" ||
        activityStatusFilter === "upcoming"
      ) {
        data = data.filter((item) => {
          if (item.completed) return false;

          const itemDateTime = new Date(`${item.date}T${item.time}`);
          const now = new Date();

          const computedStatus = itemDateTime > now ? "upcoming" : "late";
          return (
            computedStatus.toLowerCase() === activityStatusFilter.toLowerCase()
          );
        });
      }
    } else if (activeTab === "pending") {
      data = pendingData;

      if (searchName) {
        data = data.filter((item) =>
          `${item.first_name} ${item.last_name}`
            .toLowerCase()
            .includes(searchName.toLowerCase()),
        );
      }
      if (searchDate) {
        data = data.filter((item) => item.reg_date === searchDate);
      }

      if (searchDisposition) {
        data = data.filter(
          (item) =>
            (item.disposition || "").toLowerCase() ===
            searchDisposition.toLowerCase(),
        );
      }
      if (searchReferralSite) {
        data = data.filter(
          (item) =>
            (item.referral_site || "").toLowerCase() ===
            searchReferralSite.toLowerCase(),
        );
      }
    } else if (activeTab === "submitted") {
      data = finalizedData;
      if (searchName) {
        data = data.filter((item) =>
          `${item.first_name} ${item.last_name}`
            .toLowerCase()
            .includes(searchName.toLowerCase()),
        );
      }
      if (searchDate) {
        data = data.filter(
          (item) => item.finalized_at.split("T")[0] === searchDate,
        );
      }
      if (searchDisposition) {
        data = data.filter(
          (item) =>
            (item.disposition || "").toLowerCase() ===
            searchDisposition.toLowerCase(),
        );
      }
      if (searchReferralSite) {
        data = data.filter(
          (item) =>
            (item.referral_site || "").toLowerCase() ===
            searchReferralSite.toLowerCase(),
        );
      }
    }

    return data;
  };

  useEffect(() => {
    getDashboardActivities();
    getRegistrations();
  }, []);

  const goBack = () => {
    navigate("/");
  };

  return (
    <div className="flex-grow flex flex-col bg-gray-50">
      <div className="flex-grow flex flex-col max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {showConfirm === "delete" && (
          <ConfirmModal
            message={"Confirm to delete registration"}
            subMessage={"This action cannot be undone"}
            confirm={deleteRegistration}
            setShowConfirm={setShowConfirm}
          />
        )}
        {showConfirm === "save" && (
          <ConfirmModal
            message={"Confirm save registration"}
            subMessage={"This will save registration without sending an email"}
            confirm={saveRegistration}
            setShowConfirm={setShowConfirm}
          />
        )}
        {showConfirm === "finalize" && (
          <ConfirmModal
            message={"Confirm finalize registration"}
            subMessage={"This will send the email notification"}
            confirm={finalizeRegistration}
            setShowConfirm={setShowConfirm}
          />
        )}
        {showConfirm === "revert" && (
          <ConfirmModal
            message={"Confirm revert to pending"}
            subMessage={
              "This will allow you to make edits and resubmit with a new email notification"
            }
            confirm={revertToPending}
            setShowConfirm={setShowConfirm}
          />
        )}
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Admin Dashboard
          </h1>
          <div className="flex gap-2">
            <button
              onClick={() => navigate("/admin-menu")}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
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
              onClick={() => {
                sessionStorage.setItem("admin_authenticated", "true");
                navigate("/admin-register");
              }}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
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
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Register
            </button>
            <button
              onClick={goBack}
              className="inline-flex items-center gap-1 px-2 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
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
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1 px-2 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-xs font-medium"
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
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              Logout
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-grow flex flex-col bg-white rounded-lg shadow-md p-6">
          {/* Tabs */}
          <div className="flex border-b mb-6">
            <button
              onClick={() => setActiveTab("activities")}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === "activities"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Activities ({dashboardStats.total_activities})
            </button>
            <button
              onClick={() => setActiveTab("pending")}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === "pending"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Pending ({dashboardStats.pending_registrations})
            </button>
            <button
              onClick={() => setActiveTab("submitted")}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === "submitted"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Submitted ({dashboardStats.submitted_registrations})
            </button>
          </div>

          {/* Header */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-gray-900">
                {activeTab === "activities" ? "Activities" : "Registrations"}
              </h2>
              {loading && (
                <span className="text-xs text-blue-600 flex items-center gap-1">
                  <svg
                    className="animate-spin h-3 w-3"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Loading...
                </span>
              )}
            </div>
            <button
              onClick={() => handle_refresh()}
              disabled={loading}
              className="bg-gray-100 text-gray-700 py-1 px-3 rounded-md hover:bg-gray-200 transition-colors text-sm disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin h-4 w-4 text-gray-500"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Refreshing...
                </>
              ) : (
                <>
                  <svg
                    className="h-4 w-4"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  Refresh
                </>
              )}
            </button>
          </div>

          {/* Search and Filters - Mobile Responsive */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              <div className="min-w-0">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {activeTab === "activities"
                    ? "Search Activities"
                    : "Search by Name"}
                </label>
                <input
                  type="text"
                  placeholder={
                    activeTab === "activities"
                      ? "Search description or client"
                      : "e.g. smith, j"
                  }
                  value={
                    activeTab === "activities" ? activitySearchTerm : searchName
                  }
                  onChange={(e) =>
                    activeTab === "activities"
                      ? setActivitySearchTerm(e.target.value)
                      : handleNameSearch(e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{
                    height: "40px",
                    minHeight: "40px",
                    maxHeight: "40px",
                  }}
                />
              </div>
              <div className="min-w-0">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search by Date
                </label>
                <DatePicker
                  name="reg_date"
                  value={searchDate}
                  onChange={(e) => handleDateSearch(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{
                    height: "40px",
                    minHeight: "40px",
                    maxHeight: "40px",
                  }}
                />
              </div>

              <div className="min-w-0">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Disposition
                </label>
                <select
                  value={searchDisposition}
                  onChange={(e) => handleDispositionSearch(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{
                    height: "40px",
                    minHeight: "40px",
                    maxHeight: "40px",
                  }}
                >
                  <option value="">All</option>
                  {/* Most Frequently Used */}
                  {dispositions
                    .filter((d) => d.is_frequent)
                    .map((disposition) => (
                      <option key={disposition.id} value={disposition.name}>
                        {disposition.name}
                      </option>
                    ))}
                  {/* Separator */}
                  {dispositions.filter((d) => !d.is_frequent).length > 0 && (
                    <option disabled>-------</option>
                  )}
                  {/* All Others in Alphabetical Order */}
                  {dispositions
                    .filter((d) => !d.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map((disposition) => (
                      <option key={disposition.id} value={disposition.name}>
                        {disposition.name}
                      </option>
                    ))}
                </select>
              </div>

              <div className="min-w-0">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Referral Site
                </label>
                <select
                  value={searchReferralSite}
                  onChange={(e) => handleReferralSiteSearch(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{
                    height: "40px",
                    minHeight: "40px",
                    maxHeight: "40px",
                  }}
                >
                  <option value="">Select Referral Site</option>
                  {/* Most Frequently Used */}
                  {referralSites
                    .filter((s) => s.is_frequent)
                    .map((site) => (
                      <option key={site.id} value={site.name}>
                        {site.name}
                      </option>
                    ))}
                  {/* Separator */}
                  {referralSites.filter((s) => !s.is_frequent).length > 0 && (
                    <option disabled>-------</option>
                  )}
                  {/* All Others in Alphabetical Order */}
                  {referralSites
                    .filter((s) => !s.is_frequent)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map((site) => (
                      <option key={site.id} value={site.name}>
                        {site.name}
                      </option>
                    ))}
                </select>
              </div>

              {activeTab === "activities" && (
                <div className="min-w-0 md:col-span-2 xl:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={activityStatusFilter}
                    onChange={(e) => setActivityStatusFilter(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      height: "40px",
                      minHeight: "40px",
                      maxHeight: "40px",
                    }}
                  >
                    <option value="all">All Activities</option>
                    <option value="upcoming">Upcoming</option>
                    <option value="completed">Completed</option>
                    <option value="late">Late</option>
                  </select>
                </div>
              )}
            </div>

            {/* Clear All Filters Button */}
            {(searchName ||
              searchDate ||
              searchDisposition ||
              searchReferralSite ||
              activitySearchTerm ||
              activityStatusFilter !== "all") && (
              <div className="mt-4 flex justify-center">
                <button
                  onClick={clearAllFilters}
                  className="bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors text-sm"
                >
                  Clear All Filters
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* Content Area */}
          {loading && currentData.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-600">Loading {activeTab}...</div>
            </div>
          ) : (
            <div>
              {/* No Data Messages */}
              {currentData.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-600">
                    {totalRecords === 0
                      ? `No ${activeTab} found.`
                      : `No ${activeTab} match your search criteria.`}
                  </p>
                </div>
              )}

              {/* Data Display */}
              {currentData.length > 0 && (
                <>
                  {/* Performance optimized rendering */}
                  <div className="space-y-4">
                    {activeTab === "activities" ? (
                      <ActivityItems filteredData={getFilteredData()} />
                    ) : (
                      <RegistrationItems
                        activeTab={activeTab}
                        deletingId={deletingId}
                        finalizingId={finalizingId}
                        revertingId={revertingId}
                        finalizedData={finalizedData}
                        pendingData={pendingData}
                        handleDelete={handleDelete}
                        handleSave={handleSave}
                        handleFinalize={handleFinalize}
                        handleRevertToPending={handleRevertToPending}
                        filteredData={getFilteredData()}
                      />
                    )}
                  </div>

                  {/* Pagination Controls */}
                  {totalPages > 1 && <PaginationControls />}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
