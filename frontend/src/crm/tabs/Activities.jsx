import { useCallback, useEffect, useState } from "react";
import { PatientServices } from "../../services/patientServices";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import DatePicker from "../ui/DatePicker";
import toast from "react-hot-toast";
import { useDashboard } from "../../context/DashboardContext";
import { useAuth } from "../../context/AuthContext";
import { useReferences } from "../../context/ReferenceContext";
import TemplateManager from "../managers/TemplateManager";
import { CheckCircleIcon, CircleIcon, SquarePenIcon } from "lucide-react";
import { Trash } from "lucide-react";
const formatTime12Hour = (time24) => {
  const [hours, minutes] = time24.split(":");
  const hour = parseInt(hours, 10);
  const ampm = hour >= 12 ? "PM" : "AM";
  const hour12 = hour % 12 || 12; // Convert 0 to 12
  return `${hour12}:${minutes} ${ampm}`;
};

function ActivityItem({ item, editActivity, handleDeleteActivity }) {
  const { getDashboardActivities } = useDashboard();
  const { getClientActivities } = useRegistration();

  const updateActivityStatus = async (isComplete) => {
    const result = await PatientServices.update_activity(
      item.patient_id,
      item.id,
      { completed: isComplete },
    );

    if (result.success) {
      item = { ...item, completed: isComplete };
      await getDashboardActivities(item.patient_id);
      await getClientActivities(item.patient_id);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error updating activity.");

        toast.error("Photo is too large. Please choose an image under 10MB.");
      } else {
        setError("Error updating activity. Please try again.");
      }
    }
  };

  const handleToggleComplete = async (e) => {
    if (item.completed) {
      updateActivityStatus(false);
    } else {
      updateActivityStatus(true);
    }
  };

  let status;

  if (item.completed) {
    status = "Completed";
  } else {
    if (new Date(`${item.date}T${item.time}`) > new Date()) {
      status = "Upcoming";
    } else {
      status = "Late";
    }
  }
  const statusStyles = {
    Upcoming: "bg-blue-100 text-blue-800",
    in_progress: "bg-yellow-100 text-yellow-800",
    Late: "bg-red-100 text-red-800",
    Completed: "bg-green-100 text-green-800",
  };

  return (
    <div>
      <div
        key={item.id}
        id={`item-${item.id}`}
        className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow mb-3"
      >
        <div className="flex justify-between items-start">
          <div className="flex-1 min-w-0">
            <div className="flex gap-2 justify-between items-start">
              <div className="flex items-center gap-3 break-words">
                <div className="flex gap-2 justify-between items-start min-w-0">
                  <div className="text-sm text-gray-600 mb-1 text-wrap min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {item.name}
                    </h3>
                  </div>
                </div>
              </div>
              <div className="flex items-center  ml-auto">
                <span
                  className={`pl-2 pr-0  py-1 text-xs font-normal rounded-l-full rounded-r-none ${
                    statusStyles[status] || "bg-gray-100 text-gray-800"
                  }`}
                >
                  {status}
                </span>
                {/* Check icon */}
                <button
                  type="button"
                  onClick={() => handleToggleComplete()}
                  className={`top-3 right-3 p-1 rounded-l-none rounded-r-full transition-colors ${
                    statusStyles[status] || "bg-gray-100 text-gray-800"
                  }`}
                  title={item.completed ? "Mark incomplete" : "Mark complete"}
                >
                  {item.completed ? (
                    <CheckCircleIcon className="w-5 h-4" />
                  ) : (
                    <CircleIcon className="w-5 h-4" />
                  )}
                </button>
              </div>
            </div>
            <div className="flex gap-2 justify-between items-start min-w-0">
              <div className="text-sm text-gray-600 mb-1 text-wrap min-w-0">
                <p className="break-words">{item.description}</p>
              </div>
            </div>
            <div className="text-sm text-gray-700 space-y-1">
              {item.date && (
                <p>
                  <strong>Date:</strong> {item.date}
                </p>
              )}
              <div className="flex gap-2 justify-between items-center min-w-0">
                <div className="text-sm text-gray-600 mb-1 text-wrap min-w-0">
                  {item.time && (
                    <p>
                      <strong>Time:</strong> {formatTime12Hour(item.time)}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    title="Edit activity"
                    onClick={() => editActivity(item)}
                  >
                    <SquarePenIcon className="w-3 h-4" />
                  </button>
                  <button
                    type="button"
                    title="Delete activity"
                    onClick={() => handleDeleteActivity(item.id)}
                  >
                    <Trash className="w-3 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Activities({ setActiveTab, currentRegistrationId }) {
  const { userRole } = useAuth();
  const { activities, getClientActivities } = useRegistration();
  const { getDashboardActivities } = useDashboard();
  const { templates, setShowManager, showManager } = useReferences();

  const [loading, setLoading] = useState(false);
  const [editingActivityId, setEditingActivityId] = useState(null);
  const [isSavingActivity, setIsSavingActivity] = useState(false);
  const [deleteActivityId, setDeleteActivityId] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [activityForm, setActivityForm] = useState({
    date: new Date().toLocaleDateString("en-CA"), // Default to today
    time: "",
    name: "General Activity",
    description: "",
  });

  function validateForm() {
    if (!currentRegistrationId) {
      alert("Please complete the Patient tab first to save activities.");
      setActiveTab("patient");
      return false;
    }

    if (!activityForm.date || activityForm.date === "") {
      toast.error("Please select a date");
      return false;
    }

    if (!activityForm.time || activityForm.time === "") {
      toast.error("Please select a time");
      return false;
    }

    if (
      activityForm.name !== "General Activity" &&
      !templates["activity"].some((d) => d.name === activityForm.name)
    ) {
      toast.error("Please select a valid template");
      return false;
    }

    if (!activityForm.description.trim() || activityForm.description === "") {
      toast.error("Please add description");
      return false;
    }

    return true;
  }

  const saveActivity = async () => {
    if (!validateForm()) {
      return;
    }
    editingActivityId ? updateActivities() : createActivities();
  };

  const createActivities = async () => {
    setLoading(true);
    setIsSavingActivity(true);

    const result = await PatientServices.create_activity(
      currentRegistrationId,
      activityForm,
    );

    if (result.success) {
      getClientActivities(currentRegistrationId);
      getDashboardActivities();
      clearActivityForm();
      toast.success("Activity created successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error creating activity.");
      } else {
        toast.error("Error creating activity. Please try again.");
      }
    }
    setIsSavingActivity(false);
    setLoading(false);
  };

  const updateActivities = async () => {
    setLoading(true);
    setIsSavingActivity(true);

    const result = await PatientServices.update_activity(
      currentRegistrationId,
      editingActivityId,
      activityForm,
    );

    if (result.success) {
      getClientActivities(currentRegistrationId);
      getDashboardActivities();
      clearActivityForm();
      toast.success("Activity updated successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating activity.");
      } else {
        toast.error("Error updating activity. Please try again.");
      }
    }
    setIsSavingActivity(false);
    setLoading(false);
  };

  const deleteActivity = async () => {
    setLoading(true);

    const result = await PatientServices.delete_activity_by_id(
      currentRegistrationId,
      deleteActivityId,
    );

    if (result.success) {
      getClientActivities(currentRegistrationId);
      getDashboardActivities();
      toast.success("Activity deleted successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error deleting activity.");
      } else {
        toast.error("Error deleting activity. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleDeleteActivity = async (id) => {
    setDeleteActivityId(id);
    setShowDeleteConfirm(true);
  };

  const handleTemplateChange = async (templateName) => {
    const template = templates["activity"].find(
      (template) => template.name === templateName,
    );

    const content =
      activityForm.description !== ""
        ? activityForm.description
        : template
          ? template.content
          : "";

    setActivityForm((prev) => ({
      ...prev,
      name: templateName === "Select" ? "General Activity" : templateName,
      description: content,
    }));
  };

  const handleActivityChange = (e) => {
    const { name, value } = e.target;
    setActivityForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const editActivity = (activity) => {
    setActivityForm({
      date: activity.date || new Date().toLocaleDateString("en-CA"),
      time: activity.time || "",
      name: activity.name || "General Activity",
      description: activity.description || "",
    });
    setEditingActivityId(activity.id);

    // Scroll to top of activity form
    document
      .querySelector("#activities")
      ?.scrollIntoView({ behavior: "smooth" });
  };

  const clearActivityForm = () => {
    setActivityForm({
      date: new Date().toLocaleDateString("en-CA"),
      time: "",
      name: "General Activity",
      description: "",
    });
    setEditingActivityId(null);
    // setSelectedTemplate("Select");
  };

  const clearDescription = () => {
    setActivityForm((prev) => ({
      ...prev,
      description: "",
    }));
  };

  const renderActivityItem = useCallback(
    (item, index) => (
      <ActivityItem
        item={item}
        editActivity={editActivity}
        handleDeleteActivity={handleDeleteActivity}
      />
    ),
    [activities],
  );

  return (
    <div id="activities" className="scroll-mt-[20px]">
      <div className="tab-content">
        <div className="space-y-6">
          {showManager === "activity" && <TemplateManager type={showManager} />}

          {/* Activities Tab Warning */}
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
              message={"Confirm delete activity"}
              subMessage={"This action cannot be undone"}
              confirm={deleteActivity}
              setShowConfirm={setShowDeleteConfirm}
            />
          )}
          <div
            className={
              !currentRegistrationId ? "opacity-50 pointer-events-none" : ""
            }
          >
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              {editingActivityId ? "Edit Activity" : "Add Activity"}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label
                  htmlFor="activityDescription"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Date *
                </label>
                <DatePicker
                  name="date"
                  value={activityForm.date}
                  onChange={handleActivityChange}
                  className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="mm/dd/yyyy"
                />
              </div>

              <div>
                <label
                  htmlFor="activityTime"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Time
                </label>
                <div className="flex w-full">
                  <input
                    type="time"
                    id="activityTime"
                    name="time"
                    value={activityForm.time}
                    onChange={handleActivityChange}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="selectedTemplate"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Activity Template
                  </label>
                  {userRole == "admin" && (
                    <button
                      type="button"
                      onClick={() => setShowManager("activity")}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Manage Templates
                    </button>
                  )}
                </div>
                <select
                  id="selectedTemplate"
                  value={activityForm.name}
                  onChange={(e) => handleTemplateChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="General Activity">General Activity</option>
                  {activityForm.name &&
                    !templates["activity"].some(
                      (d) => d.name === activityForm.name,
                    ) &&
                    activityForm.name !== "General Activity" && (
                      <option
                        value={activityForm.name}
                        disabled
                        className="text-red-600"
                      >
                        {activityForm.name} (No longer available)
                      </option>
                    )}
                  {templates["activity"].map((template) => (
                    <option key={template.id} value={template.name}>
                      {template.name}
                    </option>
                  ))}
                </select>
                {activityForm.name &&
                  !templates["activity"].some(
                    (d) => d.name === activityForm.name,
                  ) &&
                  activityForm.name !== "General Activity" && (
                    <div className="mt-1 text-sm text-red-600">
                      ⚠️ This option is no longer available. Please select a new
                      option before saving.
                    </div>
                  )}
              </div>

              <div className="md:col-span-2">
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="activityDescription"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Description
                  </label>
                  <button
                    type="button"
                    onClick={clearDescription}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Clear
                  </button>
                </div>
                <textarea
                  id="activityDescription"
                  name="description"
                  rows={4}
                  value={activityForm.description}
                  onChange={handleActivityChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black resize-y"
                  placeholder={
                    editingActivityId
                      ? "Edit your activity content..."
                      : (activityForm.name === "General Activity") === "Select"
                        ? "Please select a template above..."
                        : `Enter activity content...`
                  }
                  style={{ whiteSpace: "pre-wrap" }}
                  autoComplete="off"
                  spellCheck="true"
                />
              </div>
            </div>

            {/* Save Buttons */}
            <div className="mt-6 grid grid-cols-2 gap-4 pb-6">
              <button
                type="button"
                onClick={saveActivity}
                disabled={
                  isSavingActivity ||
                  !activityForm.description.trim() ||
                  !currentRegistrationId
                }
                className="bg-black text-white px-6 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
              >
                {isSavingActivity
                  ? "Saving..."
                  : editingActivityId
                    ? "Update Activity"
                    : "Save Activity"}
              </button>

              <button
                type="button"
                onClick={clearActivityForm}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
              >
                Clear Form
              </button>
            </div>
          </div>
        </div>

        {/* Activities List */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Saved Activities
          </h3>

          {activities.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No activities have been saved yet.</p>
            </div>
          ) : (
            <div>{activities.map(renderActivityItem)}</div>
          )}
        </div>
      </div>
    </div>
  );
}
