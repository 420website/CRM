import { useNavigate } from "react-router-dom";
import { useCallback } from "react";
import { ObjectServices } from "../../services/objectService";
import { useState } from "react";
import toast from "react-hot-toast";

export function ActivityItems({ filteredData }) {
  const [showingPhotos, setShowingPhotos] = useState([]);
  const [loadedPhotos, setLoadedPhotos] = useState({});
  const [loadingPhotos, setLoadingPhotos] = useState(new Set());

  const getPhoto = async (registrationId) => {
    const result = await ObjectServices.get_photo_base64(registrationId);
    if (result.success) {
      return `data:image/jpeg;base64,${result.data?.file}`;
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
  loadingPhotos,
  loadedPhotos,
  showPhoto,
  hidePhoto,
  showingPhotos,
}) {
  const navigate = useNavigate();

  const isShowing = showingPhotos.some(
    ([id, idx]) => id === item.patient_id && idx === index,
  );

  const status =
    new Date(`${item.date}T${item.time}`) > new Date()
      ? "upcoming"
      : "completed";

  return (
    <div
      key={item.id}
      className="border rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {item.description}
            </h3>
            <span
              className={`px-2 py-1 text-xs font-medium rounded-full ${
                status === "upcoming"
                  ? "bg-blue-100 text-blue-800"
                  : "bg-green-100 text-green-800"
              }`}
            >
              {status === "upcoming" ? "Upcoming" : "Completed"}
            </span>
          </div>
          <div className="text-sm text-gray-600 mt-1">
            <p className="font-medium">
              Client: {item.first_name} {item.last_name}
              {item.disposition && (
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs font-normal ml-2">
                  {item.disposition.charAt(0).toUpperCase() +
                    item.disposition.slice(1).toLowerCase()}
                </span>
              )}
            </p>
            <p>Date: {item.date}</p>
            {item.time && <p>Time: {item.time}</p>}
            {item.phone1 && <p>Phone: {item.phone1}</p>}
            <p className="text-xs text-gray-500 mt-1">Activity ID: {item.id}</p>
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

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => {
            navigate(`/admin-edit/${item.patient_id}`);
          }}
          className="bg-black hover:bg-gray-800 text-white py-2 px-4 rounded-md transition-colors text-xs font-medium"
        >
          View Client Profile
        </button>
      </div>
    </div>
  );
}
