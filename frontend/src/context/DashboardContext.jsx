import { createContext, useContext, useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import { PatientServices } from "../services/patientServices";
import toast from "react-hot-toast";

const DashboardContext = createContext();

export const useDashboard = () => useContext(DashboardContext);

export function DashboardProvider({ children }) {
  const { userRole } = useAuth();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastItem, setLastItem] = useState(null);
  const [activeTab, setActiveTab] = useState(
    userRole !== "limited" ? "activities" : "submitted",
  );

  // Search and filter state
  const [searchName, setSearchName] = useState("");
  const [searchDate, setSearchDate] = useState("");
  const [searchDisposition, setSearchDisposition] = useState("");
  const [searchReferralSite, setSearchReferralSite] = useState("");
  const [activitySearchTerm, setActivitySearchTerm] = useState("");
  const [activityStatusFilter, setActivityStatusFilter] = useState("all");
  const [searchMonth, setSearchMonth] = useState("");
  const [searchEndDate, setSearchEndDate] = useState(null);

  // Data state - now paginated
  const [pendingData, setPendingData] = useState([]);
  const [finalizedData, setFinalizedData] = useState([]);
  const [activityData, setActivityData] = useState([]);
  const [filteredActivity, setFilteredActivity] = useState([]);
  const [filteredPending, setFilteredPending] = useState([]);
  const [filteredSubmitted, setFilteredSubmitted] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    pending_registrations: 0,
    submitted_registrations: 0,
    total_activities: 0,
  });

  const resetActiveTab = () => {
    setActiveTab(userRole !== "limited" ? "activities" : "submitted");
  };

  // -- Filters
  const clearAllFilters = () => {
    setSearchName("");
    setSearchDate("");
    setSearchEndDate(null);
    setSearchMonth("");
    setSearchDisposition("");
    setSearchReferralSite("");
    setActivitySearchTerm("");
    setActivityStatusFilter("all");
    setFilteredActivity(activityData);
    setFilteredPending(pendingData);
    setFilteredSubmitted(finalizedData);
  };

  const clearActivityFilters = () => {
    setSearchDate("");
    setSearchDisposition("");
    setSearchReferralSite("");
    setActivitySearchTerm("");
    setActivityStatusFilter("all");
    setFilteredActivity(activityData);
  };

  const clearRegistrationFilters = () => {
    setSearchName("");
    setSearchDate("");
    setSearchDisposition("");
    setSearchReferralSite("");
    setFilteredPending(pendingData);
    setFilteredSubmitted(finalizedData);
  };

  // Optimized search handlers
  const handleNameSearch = (value) => {
    setSearchName(value);
  };

  const handleDateSearch = (value) => {
    if (value) {
      setSearchDate(value);
    } else {
      setSearchDate(value);
      setSearchEndDate(value);
    }
  };

  const handleEndDateSearch = (value) => {
    setSearchEndDate(value);
  };

  const handleMonthSearch = (value) => {
    setSearchMonth(value);
  };

  const handleDispositionSearch = (value) => {
    setSearchDisposition(value);
  };

  const handleReferralSiteSearch = (value) => {
    setSearchReferralSite(value);
  };

  const handleActivityTermSearch = (value) => {
    setActivitySearchTerm(value);
  };

  const handleActivityStatusSearch = (value) => {
    setActivityStatusFilter(value);
  };

  const filterActivity = () => {
    let data = activityData;

    const hasActiveFilters =
      searchName ||
      searchEndDate ||
      searchMonth ||
      searchDate ||
      searchDisposition ||
      searchReferralSite ||
      activitySearchTerm ||
      (activityStatusFilter && activityStatusFilter !== "all");

    if (hasActiveFilters) {
      if (activitySearchTerm) {
        const terms = activitySearchTerm.toLowerCase().trim().split(/\s+/);

        data = data.filter((item) => {
          const haystack =
            `${item.first_name ?? ""} ${item.last_name ?? ""} ${item.description ?? ""}i ${item.name}`.toLowerCase();
          return terms.every((term) => haystack.includes(term));
        });
      }

      if (searchDate && (!searchEndDate || searchDate === searchEndDate)) {
        data = data.filter((item) => item.date === searchDate);
      }

      if (searchDate && searchEndDate) {
        data = data.filter(
          (item) => searchDate <= item.date && item.date <= searchEndDate,
        );
      }

      if (searchMonth) {
        data = data.filter((item) => item.date.startsWith(searchMonth));
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
    }

    setFilteredActivity(data);
  };

  const filterPending = () => {
    let data = pendingData;

    const hasActiveFilters =
      searchName ||
      searchDate ||
      searchEndDate ||
      searchMonth ||
      searchDisposition ||
      searchReferralSite;

    if (hasActiveFilters) {
      if (searchName) {
        data = data.filter((item) =>
          `${item.first_name} ${item.last_name}`
            .toLowerCase()
            .includes(searchName.toLowerCase()),
        );
      }

      if (searchDate && (!searchEndDate || searchDate === searchEndDate)) {
        data = data.filter(
          (item) =>
            new Date(item.created_at).toLocaleDateString("en-CA") ===
            searchDate,
        );
      }

      if (searchDate && searchEndDate) {
        data = data.filter((item) => {
          const date = new Date(item.created_at).toLocaleDateString("en-CA");
          return searchDate <= date && date <= searchEndDate;
        });
      }

      if (searchMonth) {
        data = data.filter((item) => {
          const date = new Date(item.created_at).toLocaleDateString("en-CA");
          return date.startsWith(searchMonth);
        });
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
    setFilteredPending(data);
  };

  const filterSubmitted = () => {
    let data = finalizedData;

    const hasActiveFilters =
      searchName ||
      searchDate ||
      searchEndDate ||
      searchMonth ||
      searchDisposition ||
      searchReferralSite;

    if (hasActiveFilters) {
      if (searchName) {
        data = data.filter((item) =>
          `${item.first_name} ${item.last_name}`
            .toLowerCase()
            .includes(searchName.toLowerCase()),
        );
      }

      if (searchDate && (!searchEndDate || searchDate === searchEndDate)) {
        data = data.filter(
          (item) =>
            new Date(item.created_at).toLocaleDateString("en-CA") ===
            searchDate,
        );
      }

      if (searchDate && searchEndDate) {
        data = data.filter((item) => {
          const date = new Date(item.created_at).toLocaleDateString("en-CA");
          return searchDate <= date && date <= searchEndDate;
        });
      }

      if (searchMonth) {
        data = data.filter((item) => {
          const date = new Date(item.created_at).toLocaleDateString("en-CA");
          return date.startsWith(searchMonth);
        });
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
    setFilteredSubmitted(data);
  };

  useEffect(() => {
    if (activeTab === "activities") {
      filterActivity();
      filterPending();
      filterSubmitted();
    } else if (activeTab === "pending") {
      filterPending();
      filterActivity();
      filterSubmitted();
    } else {
      filterSubmitted();
      filterPending();
      filterActivity();
    }
  }, [
    searchName,
    searchDate,
    searchEndDate,
    searchMonth,
    searchDisposition,
    searchReferralSite,
    activitySearchTerm,
    activityStatusFilter,
    activityData,
    pendingData,
    finalizedData,
  ]);

  useEffect(() => {
    setDashboardStats({
      pending_registrations:
        activeTab === "pending" ? filteredPending.length : pendingData.length,
      submitted_registrations:
        activeTab === "submitted"
          ? filteredSubmitted.length
          : finalizedData.length,
      total_activities:
        activeTab === "activities"
          ? filteredActivity.length
          : activityData.length,
    });
  }, [
    activeTab,
    activityData,
    pendingData,
    finalizedData,
    filteredActivity,
    filteredSubmitted,
    filteredPending,
  ]);

  // -- Dashboard Data
  const getDashboardActivities = async () => {
    setLoading(true);
    setError("");

    if (userRole !== "limited") {
      const result = await PatientServices.get_activities();

      if (result.success) {
        setActivityData(result.data);
      } else {
        if (result.status === 400 || result.status === 409) {
          setError(result.message || "Invalid credentials.");
        } else {
          setError("Login failed. Please try again.");
        }
      }
    }
    setLoading(false);
  };

  // Pending and Submitted
  const getDashboardRegistrations = async () => {
    setLoading(true);
    setError("");

    const result = await PatientServices.get_patients();

    if (result.success) {
      if (userRole !== "limited") {
        const pending = result.data.filter((reg) => reg.status === "pending");
        setPendingData(pending);
      }

      let finalized = result.data.filter(
        (reg) => reg.status === "finalized" || reg.status === "saved",
      );

      if (userRole === "limited") {
        finalized = finalized.filter((reg) => !reg.limited);
      }
      setFinalizedData(finalized);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    const getInitialData = async () => {
      getDashboardActivities();
      getDashboardRegistrations();
    };

    getInitialData();
  }, []);

  // -- Actions
  const deleteRegistration = async (id) => {
    const result = await PatientServices.delete_patient_by_id(id);

    if (result.success) {
      getDashboardActivities();
      getDashboardRegistrations();
      toast.success("Registration deleted successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting patient.");
      } else {
        toast.error("Error deleting patient. Please try again.");
      }
    }
  };

  const finalizeRegistration = async (id) => {
    setError(null);

    const result = await PatientServices.update_patient_status(id, {
      status: "finalized",
    });

    if (result.success) {
      getDashboardActivities();
      getDashboardRegistrations();
      toast.success("Registration finalized successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating patient status.");
      } else {
        toast.error("Error updating patient status. Please try again.");
      }
    }
  };

  const saveRegistration = async (id) => {
    setError(null);

    const result = await PatientServices.update_patient_status(id, {
      status: "saved",
    });

    if (result.success) {
      getDashboardActivities();
      getDashboardRegistrations();
      toast.success("Registration saved successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating patient status.");
      } else {
        toast.error("Error updating patient status. Please try again.");
      }
    }
  };

  const revertToPending = async (id) => {
    setError(null);

    const result = await PatientServices.update_patient_status(id, {
      status: "pending",
    });

    if (result.success) {
      getDashboardActivities();
      getDashboardRegistrations();
      toast.success("Registration reverted to pending");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating patient status.");
      } else {
        toast.error("Error updating patient status. Please try again.");
      }
    }
  };

  // Activity Actions
  const updateActivity = async (patient_id, activity_id, data) => {
    const result = await PatientServices.update_activity(
      patient_id,
      activity_id,
      data,
    );

    if (result.success) {
      await getDashboardActivities();
      toast.success("Activity updated successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating activity.");
      } else {
        toast.error("Error updating activity. Please try again.");
      }
    }
  };

  const deleteActivity = async (patient_id, activity_id) => {
    const result = await PatientServices.delete_activity_by_id(
      patient_id,
      activity_id,
    );

    if (result.success) {
      await getDashboardActivities();
      toast.success("Activity deleted successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting activity.");
      } else {
        toast.error("Error deleting activity. Please try again.");
      }
    }
  };

  return (
    <DashboardContext.Provider
      value={{
        activeTab,
        setActiveTab,
        dashboardStats,
        getDashboardRegistrations,
        getDashboardActivities,
        pendingData,
        finalizedData,
        activityData,
        clearActivityFilters,
        clearRegistrationFilters,
        searchName,
        searchReferralSite,
        searchDate,
        searchEndDate,
        searchMonth,
        searchDisposition,
        activitySearchTerm,
        activityStatusFilter,
        handleDateSearch,
        handleNameSearch,
        handleDispositionSearch,
        handleReferralSiteSearch,
        handleActivityTermSearch,
        handleActivityStatusSearch,
        saveRegistration,
        deleteRegistration,
        finalizeRegistration,
        revertToPending,
        filteredActivity,
        filteredSubmitted,
        filteredPending,
        lastItem,
        setLastItem,
        updateActivity,
        deleteActivity,
        resetActiveTab,
        clearAllFilters,
        handleEndDateSearch,
        handleMonthSearch,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}
