import { useNavigate } from "react-router-dom";
import { useCallback } from "react";
import { ObjectServices } from "../../services/objectService";
import { useState } from "react";
import toast from "react-hot-toast";
import { useRegistration } from "../../context/RegistrationContext";
import { PatientServices } from "../../services/patientServices";
import { CheckCircleIcon, CircleIcon, SquarePenIcon } from "lucide-react";
import DatePicker from "./DatePicker";

export function ActivityItems({ filteredData }) {
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

  const renderActivityItem = useCallback(
    (item, index) => (
      <ActivityItem
        key={index}
        index={index}
        item={item}
        activityId={item.id}
        loadedPhotos={loadedPhotos}
        loadingPhotos={loadingPhotos}
        showPhoto={showPhoto}
        hidePhoto={hidePhoto}
        showingPhotos={showingPhotos}
      />
    ),
    [loadedPhotos, loadingPhotos, showPhoto, hidePhoto, showingPhotos],
  );

  return <div>{filteredData.map(renderActivityItem)}</div>;
}

export default function ActivityItem({
  index,
  item,
  activityId,
  loadingPhotos,
  loadedPhotos,
  showPhoto,
  hidePhoto,
  showingPhotos,
}) {
  const navigate = useNavigate();
  const { getDashboardActivities, activityData } = useRegistration();
  const activity = activityData.find((activity) => activity.id === activityId);
  const [isEditing, setIsEditing] = useState(false);

  const updateActivityStatus = async (isComplete) => {
    const result = await PatientServices.update_activity(
      item.patient_id,
      item.id,
      { completed: isComplete },
    );

    if (result.success) {
      item = { ...item, completed: isComplete };
      getDashboardActivities();
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
        className="relative border rounded-lg  bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer mb-2"
      >
        <div className="flex justify-between items-center  m-4 ml-2 mb-0 ">
          {item.disposition && (
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-normal ">
              {item.disposition.charAt(0).toUpperCase() +
                item.disposition.slice(1).toLowerCase()}
            </span>
          )}
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
        <div className="flex justify-between items-start pl-4 pr-4 ">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2 break-all">
              <h3 className="text-lg font-semibold text-gray-900">
                {item.description}
              </h3>
            </div>
            <div className="text-sm text-gray-600 mt-1">
              <p className="font-medium">
                Client: {item.first_name} {item.last_name}
              </p>
              <p>Date: {item.date}</p>
              {item.time && <p>Time: {item.time}</p>}
              {item.phone1 && <p>Phone: {item.phone1}</p>}
              <p className="text-xs text-gray-500 mt-1">
                Activity ID: {item.id}
              </p>
            </div>

            {/* Lazy loaded photo */}
            {isShowing && (
              <div className="mt-4 mb-4">
                <div className="flex flex-row justify-between sm:flex-row">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Uploaded Photo:
                  </p>
                  <button
                    className="text-sm font-medium text-gray-700 mb-2"
                    onClick={() => hidePhoto(item.patient_id, index)}
                  >
                    x
                  </button>
                </div>
                <img
                  src={loadedPhotos[item.patient_id]}
                  alt="Registration photo"
                  className="lg:max-w-xs md:w-3/4 max-h-48 object-contain border rounded"
                  onError={(e) => {
                    e.target.style.display = "none";
                  }}
                />
              </div>
            )}

            {!isShowing && (
              <button
                onClick={() => showPhoto(item.patient_id, index)}
                className="mt-2 text-sm text-blue-600 hover:text-blue-800"
              >
                Show Photo
              </button>
            )}

            {loadingPhotos.has(item.patient_id) && (
              <div className="mt-2 text-sm text-gray-500">Loading photo...</div>
            )}
          </div>
        </div>

        <div className="flex gap-2 mt-4 p-4 pt-0 justify-between">
          <button
            onClick={() => {
              navigate(`/admin-edit/${item.patient_id}`);
            }}
            className="bg-black hover:bg-gray-800 text-white py-2 px-4 rounded-md transition-colors text-xs font-medium"
          >
            View Client Profile
          </button>
          <button onClick={handleEdit}>
            <SquarePenIcon className="w-3 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function EditActivityItem({ index, item, activityData, setIsEditing }) {
  const { getDashboardActivities } = useRegistration();

  const [activityForm, setActivityForm] = useState({
    date: activityData.date,
    time: activityData.time,
    description: activityData.description,
  });

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

  const updateActivities = async () => {
    if (!validateForm()) {
      return;
    }

    const result = await PatientServices.update_activity(
      item.patient_id,
      item.id,
      activityForm,
    );

    if (result.success) {
      getDashboardActivities();
      setIsEditing(false);
      toast.success("Activity updated successfully");
    } else {
      if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Error updating activity.");
      } else {
        toast.error("Error updating activity. Please try again.");
      }
    }
  };

  const deleteActivity = async () => {
    const result = await PatientServices.delete_activity_by_id(
      item.patient_id,
      item.id,
    );

    if (result.success) {
      getDashboardActivities();
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
    <div
      key={item.id}
      className="relative border rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer mb-2"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
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

          <div className="flex gap-3">
            <button
              type="button"
              onClick={updateActivities}
              className="bg-black text-white text-xs px-4 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              Update
            </button>
            <button
              type="button"
              onClick={deleteActivity}
              className="bg-black text-white px-4 text-xs py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              Delete
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
