import { useState } from "react";
import { PatientServices } from "../../services/patientServices";
import ConfirmModal from "../components/ConfirmModal";
import { useRegistration } from "../../context/RegistrationContext";
import DatePicker from "../ui/DatePicker";
import toast from "react-hot-toast";
import { useDashboard } from "../../context/DashboardContext";

export default function Activities({ setActiveTab, currentRegistrationId }) {
  const { activities, getActivities } = useRegistration();
  const { getDashboardActivities } = useDashboard();
  const [loading, setLoading] = useState(false);
  const [editingActivityId, setEditingActivityId] = useState(null);
  const [isSavingActivity, setIsSavingActivity] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteActivityId, setDeleteActivityId] = useState(null);
  const [activityForm, setActivityForm] = useState({
    date: new Date().toLocaleDateString("en-CA"), // Default to today
    time: "",
    description: "",
  });

  function validateForm() {
    if (!currentRegistrationId) {
      alert("Please complete the Patient tab first to save notes.");
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
      getActivities(currentRegistrationId);
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
      getActivities(currentRegistrationId);
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
      getActivities(currentRegistrationId);
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
      description: activity.description || "",
    });
    setEditingActivityId(activity.id);

    // Scroll to top of activity form
    document.querySelector("#tabs")?.scrollIntoView({ behavior: "smooth" });
  };

  const clearActivityForm = () => {
    setActivityForm({
      date: new Date().toLocaleDateString("en-CA"),
      time: "",
      description: "",
    });
    setEditingActivityId(null);
  };

  return (
    <div>
      <div className="tab-content">
        <div className="space-y-6">
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
                <label
                  htmlFor="activityDescription"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Description
                </label>
                <textarea
                  id="activityDescription"
                  name="description"
                  rows={4}
                  value={activityForm.description}
                  onChange={handleActivityChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black resize-y"
                  placeholder="Enter activity description..."
                />
              </div>

              {/* Save Buttons */}
              <div className="flex gap-3">
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
                {editingActivityId && (
                  <button
                    type="button"
                    onClick={clearActivityForm}
                    className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Cancel Edit
                  </button>
                )}
                <button
                  type="button"
                  onClick={clearActivityForm}
                  className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400 transition-colors"
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
              <div className="space-y-3">
                {activities.map((activity, index) => (
                  <div
                    key={activity.id}
                    className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between m-4 ml-2 mb-0">
                      {(() => {
                        if (activity.completed) {
                          return (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                              Completed
                            </span>
                          );
                        } else {
                          if (
                            new Date(`${activity.date}T${activity.time}`) >
                            new Date()
                          ) {
                            return (
                              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                                Upcoming
                              </span>
                            );
                          } else {
                            return (
                              <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                                Late
                              </span>
                            );
                          }
                        }
                      })()}
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => editActivity(activity)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                          title="Edit activity"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDeleteActivity(activity.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                          title="Delete activity"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                    <div className="flex p-4 pt-0 justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg font-semibold text-gray-900 break-all">
                            {activity.description}
                          </span>
                        </div>
                        <div className="text-sm text-gray-700 space-y-1">
                          {activity.date && (
                            <p>
                              <strong>Date:</strong> {activity.date}
                            </p>
                          )}
                          {activity.time && (
                            <p>
                              <strong>Time:</strong> {activity.time}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
