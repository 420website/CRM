import { useNavigate } from "react-router-dom";
import { useCallback, useEffect, useRef } from "react";
import { ObjectServices } from "../../services/objectService";
import { useState } from "react";
import toast from "react-hot-toast";
import { PatientServices } from "../../services/patientServices";
import { CheckCircleIcon, CircleIcon, SquarePenIcon } from "lucide-react";
import DatePicker from "./DatePicker";
import { useDashboard } from "../../context/DashboardContext";
import { useReferences } from "../../context/ReferenceContext";

export function ActivityItems({
  handleSave,
  handleDelete,
  handleFinalize,
  handleRevertToPending,
}) {
  const { filteredActivity, lastItem, setLastItem } = useDashboard();

  const [showingPhotos, setShowingPhotos] = useState([]);
  const [loadedPhotos, setLoadedPhotos] = useState({});
  const [loadingPhotos, setLoadingPhotos] = useState(new Set());

  const getPhoto = async (registrationId) => {
    const result = await ObjectServices.get_photo_raw(registrationId);

    if (result.success) {
      const blob = new Blob([result.data], { type: "image/jpeg" });
      const url = URL.createObjectURL(blob);
      return url;
    } else {
      toast.error("No photo found for this registration.");
    }
  };

  const showPhoto = async (patientId, index) => {
    if (loadedPhotos[patientId]) {
      const isShowing = showingPhotos.some(
        ([id, idx]) => id === patientId && idx === index,
      );

      if (!isShowing) {
        setShowingPhotos([...showingPhotos, [patientId, index]]);
        return;
      }
      return;
    }

    const photo = await getPhoto(patientId);

    if (photo) {
      setLoadedPhotos((prev) => ({
        ...prev,
        [patientId]: photo,
      }));
      setShowingPhotos([...showingPhotos, [patientId, index]]);
    }
  };

  const hidePhoto = async (patientId, index) => {
    setShowingPhotos((prev) =>
      prev.filter(([id, idx]) => !(id === patientId && idx === index)),
    );
  };

  useEffect(() => {
    if (lastItem && filteredActivity.length > 0) {
      setTimeout(() => {
        document
          .getElementById(`item-${lastItem}`)
          ?.scrollIntoView({ behavior: "smooth" });
        setLastItem(null); // Clear after scrolling
      }, 300);
    }
  }, []);

  const renderActivityItem = useCallback(
    (item, index) => (
      <ActivityItem
        key={index}
        index={index}
        item={item}
        activityId={item.id}
        loadedPhotos={loadedPhotos}
        loadingPhotos={loadingPhotos}
        handleDelete={handleDelete}
        handleSave={handleSave}
        handleFinalize={handleFinalize}
        handleRevertToPending={handleRevertToPending}
        showPhoto={showPhoto}
        hidePhoto={hidePhoto}
        showingPhotos={showingPhotos}
      />
    ),
    [
      loadedPhotos,
      loadingPhotos,
      showPhoto,
      hidePhoto,
      showingPhotos,
      filteredActivity,
    ],
  );

  return <div>{filteredActivity.map(renderActivityItem)}</div>;
}

export default function ActivityItem({
  index,
  item,
  activityId,
  loadingPhotos,
  loadedPhotos,
  handleDelete,
  handleSave,
  handleFinalize,
  handleRevertToPending,
  showPhoto,
  hidePhoto,
  showingPhotos,
}) {
  // Check stops error if activity item deleted
  const { getDashboardActivities, activityData, setLastItem } = useDashboard();
  const activity = activityData.find((activity) => activity.id === activityId);
  if (!activity) return null;

  const navigate = useNavigate();
  const nameRef = useRef(null);
  const [nameOnOneLine, setNameOnOneLine] = useState(true);
  const [isEditing, setIsEditing] = useState(false);

  const updateActivityStatus = async (isComplete) => {
    const result = await PatientServices.update_activity(
      item.patient_id,
      item.id,
      { completed: isComplete },
    );

    if (result.success) {
      item = { ...item, completed: isComplete };
      await getDashboardActivities();
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
    if (activity.completed) {
      updateActivityStatus(false);
    } else {
      updateActivityStatus(true);
    }
  };

  const handleEdit = async () => {
    setIsEditing(!isEditing);
  };

  const isShowing = showingPhotos.some(
    ([id, idx]) => id === item.patient_id && idx === index,
  );

  let status;

  if (activity.completed) {
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

  useEffect(() => {
    if (nameRef.current) {
      // Small delay to ensure layout is complete
      const timer = setTimeout(() => {
        const height = nameRef.current.offsetHeight;
        const lineHeight = parseFloat(
          getComputedStyle(nameRef.current).lineHeight,
        );
        setNameOnOneLine(height <= lineHeight * 1.5);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [item.first_name, item.last_name]);

  return (
    <div>
      {isEditing && (
        <EditActivityItem
          index={index}
          item={item}
          activityData={activity}
          setIsEditing={setIsEditing}
        />
      )}
      <div
        key={item.id}
        id={`item-${item.id}`}
        className="relative border rounded-lg  bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer mb-2 scroll-mt-[20px] p-4"
      >
        <div className="flex justify-between items-start">
          <div className="flex-1 min-w-0">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3 break-all">
                <div className="flex gap-2 items-center">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {item.name}
                  </h3>
                  <button onClick={handleEdit}>
                    <SquarePenIcon className="w-3 h-4" />
                  </button>
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
            <div>
              <div className="text-sm text-gray-600 mb-1 text-wrap">
                <p className="break-words">{item.description}</p>
              </div>
            </div>
            <div className="flex justify-between items-start ">
              <div className="flex-1  min-w-0">
                <div className="flex justify-between items-start gap-2 min-w-0">
                  <h3
                    ref={nameRef}
                    className="text-lg font-semibold text-gray-900 min-w-0 break-words"
                  >
                    {nameOnOneLine ? (
                      <>
                        <span>{item.first_name}</span>{" "}
                        <span>{item.last_name}</span>
                      </>
                    ) : (
                      <>
                        <span>{item.first_name}</span>
                        <br />
                        <span>{item.last_name}</span>
                      </>
                    )}
                  </h3>
                  {item.disposition && (
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs font-normal whitespace-nowrap shrink-0">
                      {item.disposition.charAt(0).toUpperCase() +
                        item.disposition.slice(1).toLowerCase()}
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  <p className="text-xs text-gray-500 mt-1">
                    {`File: ${item.file_id || "N/A"} ID: ${item.id}`}
                  </p>
                  <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
                    {`
              Registration Date: ${
                new Date(item.submitted_date).toLocaleDateString("en-CA") ||
                "Not provided"
              }`}
                  </p>
                  <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
                    Submitted: {new Date(item.submitted_date).toLocaleString()}
                  </p>
                  {(item.status === "finalized" || item.status === "saved") &&
                    item.finalized_at && (
                      <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
                        Finalized:{" "}
                        {new Date(item.finalized_at).toLocaleString()}
                      </p>
                    )}
                </div>
                {!isShowing && (
                  <button
                    onClick={() => showPhoto(item.patient_id, index)}
                    className="flex justify-start mt-2 mb-2 text-sm text-blue-600 hover:text-blue-800"
                  >
                    Show Photo
                  </button>
                )}
                {isShowing && (
                  <button
                    onClick={() => hidePhoto(item.patient_id, index)}
                    className="flex justify-start mt-2 mb-2 text-sm text-blue-600 hover:text-blue-800"
                  >
                    Hide Photo
                  </button>
                )}
              </div>
            </div>

            {/* Photo and buttons*/}
            <div
              className={`flex gap-2 justify-between ${isShowing ? "flex-row" : "flex-col"}`}
            >
              {/* Lazy loaded photo */}
              {isShowing && (
                <div className="flex-grow">
                  <img
                    src={loadedPhotos[item.patient_id]}
                    alt="Registration photo"
                    className="w-64 h-48 object-cover border rounded"
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
                  />
                </div>
              )}

              {loadingPhotos.has(item.id) && (
                <div className="mt-2 text-sm text-gray-500">
                  Loading photo...
                </div>
              )}

              {/* Action Buttons - Horizontal layout with intuitive colors */}
              <div
                className={`flex gap-2  ${isShowing ? "flex-col" : "flex-row"}`}
              >
                <button
                  onClick={() => handleDelete(item.patient_id, item.id)}
                  className={`bg-red-600 hover:bg-red-700 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]`}
                >
                  Delete
                </button>
                <button
                  onClick={() => {
                    setLastItem(item.id);
                    navigate(`/admin-edit/${item.patient_id}`);
                  }}
                  className={`bg-black hover:bg-gray-800 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium flex-1 min-w-[60px]`}
                >
                  Edit
                </button>
                {item.status === "pending" && (
                  <>
                    <button
                      onClick={() => {
                        hidePhoto(item.patient_id, index);
                        handleSave(item.patient_id);
                      }}
                      className={`bg-black hover:bg-gray-800 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]`}
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        hidePhoto(item.patient_id, index);
                        handleFinalize(item.patient_id);
                      }}
                      className={`bg-green-600 hover:bg-green-700 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]`}
                    >
                      Submit
                    </button>
                  </>
                )}

                {(item.status === "saved" || item.status === "finalized") && (
                  <button
                    onClick={() => handleRevertToPending(item.patient_id)}
                    className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]"
                  >
                    Back To Pending
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function EditActivityItem({ index, item, activityData, setIsEditing }) {
  const { updateActivity, deleteActivity } = useDashboard();
  const { templates } = useReferences();

  const [activityForm, setActivityForm] = useState({
    date: activityData.date,
    time: activityData.time,
    name: activityData.name,
    description: activityData.description,
  });

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

  const clearDescription = () => {
    setActivityForm((prev) => ({
      ...prev,
      description: "",
    }));
  };

  const handleActivityChange = (e) => {
    const { name, value } = e.target;
    setActivityForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const closeEdit = () => {
    setIsEditing(false);
  };

  function validateForm() {
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

  const handleEdit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      await updateActivity(item.patient_id, item.id, activityForm);
      setIsEditing(false);
    } catch (error) {
      toast.error(error);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteActivity(item.patient_id, item.id);
      setIsEditing(false);
    } catch (error) {
      toast.error(error);
    }
  };

  return (
    <div
      key={item.id}
      className="relative border rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer mb-2"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div>
            <label
              htmlFor="activityDescription"
              className="block text-sm font-medium text-gray-700 mb-1"
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
              className="block text-sm font-medium text-gray-700 mt-1 mb-1 "
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
            <div className="flex items-center justify-between mt-1 mb-1">
              <label
                htmlFor="selectedTemplate"
                className="block text-sm font-medium text-gray-700"
              >
                Activity Template
              </label>
            </div>
            <select
              id="selectedTemplate"
              value={activityForm.name}
              onChange={(e) => handleTemplateChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
            >
              <option value="General Activity">General Activity</option>
              {templates["activity"].map((template) => (
                <option key={template.id} value={template.name}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="flex items-center justify-between mt-1 mb-1">
              <label
                htmlFor="activityDescription"
                className="block text-sm font-medium text-gray-700"
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
              placeholder="Enter activity description..."
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleEdit}
              className="bg-black text-white text-xs px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              Update
            </button>
            <button
              type="button"
              onClick={closeEdit}
              className="bg-gray-300 text-gray-700 text-xs px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
