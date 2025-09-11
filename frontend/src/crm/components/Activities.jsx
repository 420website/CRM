import { useState, useEffect } from "react";
import { PatientServices } from "../../services/patientServices";

export default function Activities({ setActiveTab, currentRegistrationId }) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [editingActivityId, setEditingActivityId] = useState(null);
  const [isSavingActivity, setIsSavingActivity] = useState(false);
  const [savedActivities, setSavedActivities] = useState([]);

  const [activityData, setActivityData] = useState({
    date: new Date().toISOString().split("T")[0], // Default to today
    time: "",
    description: "",
  });

  const saveActivity = async () => {
    editingActivityId ? updateActivities() : createActivities();
  };

  const getActivities = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_activities_by_patient(registrationId);
    if (result.success) {
      setSavedActivities(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const createActivities = async () => {
    setLoading(true);
    setError("");

    if (!currentRegistrationId) {
      alert("Please complete the Client tab first to save activities.");
      setActiveTab("client");
      return;
    }

    if (!activityData.description.trim()) {
      alert("Please enter an activity description before saving");
      return;
    }

    setIsSavingActivity(true);

    const result = await PatientServices.create_activity(
      currentRegistrationId,
      activityData,
    );

    if (result.success) {
      await getActivities(currentRegistrationId);
      clearActivityForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setIsSavingActivity(false);
    setLoading(false);
  };

  const updateActivities = async () => {
    setLoading(true);
    setError("");

    if (!currentRegistrationId) {
      alert("Please complete the Client tab first to save activities.");
      setActiveTab("client");
      return;
    }

    if (!activityData.description.trim()) {
      alert("Please enter an activity description before saving");
      return;
    }

    setIsSavingActivity(true);

    const result = await PatientServices.update_activity(
      currentRegistrationId,
      editingActivityId,
      activityData,
    );

    if (result.success) {
      await getActivities(currentRegistrationId);
      clearActivityForm();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setIsSavingActivity(false);
    setLoading(false);
  };

  const deleteActivity = async (activityId) => {
    if (!window.confirm("Are you sure you want to delete this activity?")) {
      return;
    }

    setLoading(true);
    setError("");

    const result = await PatientServices.delete_activity_by_id(
      currentRegistrationId,
      activityId,
    );

    if (result.success) {
      await getActivities(currentRegistrationId);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleActivityChange = (e) => {
    const { name, value } = e.target;
    setActivityData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  useEffect(() => {
    if (currentRegistrationId) {
      getActivities(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  const editActivity = (activity) => {
    setActivityData({
      date: activity.date || new Date().toISOString().split("T")[0],
      time: activity.time || "",
      description: activity.description || "",
    });
    setEditingActivityId(activity.id);
    // Scroll to top of activity form
    document
      .querySelector("#activityDescription")
      ?.scrollIntoView({ behavior: "smooth" });
  };

  const clearActivityForm = () => {
    setActivityData({
      date: new Date().toISOString().split("T")[0],
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
                  Description *
                </label>
                <input
                  type="date"
                  id="activityDate"
                  name="date"
                  value={activityData.date}
                  onChange={handleActivityChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label
                  htmlFor="activityTime"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Time
                </label>
                <input
                  type="time"
                  id="activityTime"
                  name="time"
                  value={activityData.time}
                  onChange={handleActivityChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
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
                  value={activityData.description}
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
                    !activityData.description.trim() ||
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

            {savedActivities.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No activities have been saved yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {savedActivities.map((activity, index) => (
                  <div
                    key={activity.id}
                    className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg font-semibold text-gray-900">
                            {activity.description}
                          </span>
                          {/* Recent indicator */}
                          {(() => {
                            const activityDateTime = new Date(
                              activity.date + "T" + (activity.time || "00:00"),
                            );
                            const now = new Date();
                            const diffHours =
                              (now - activityDateTime) / (1000 * 60 * 60);
                            if (diffHours < 24) {
                              return (
                                <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                                  Recent
                                </span>
                              );
                            }
                            return null;
                          })()}
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
                          onClick={() => deleteActivity(activity.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                          title="Delete activity"
                        >
                          Delete
                        </button>
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
