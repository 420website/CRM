import { useNavigate } from "react-router-dom";
import { ObjectServices } from "../../services/objectService";

export default function RegistrationItem({
  activeTab,
  item,
  setLoadedPhotos,
  loadingPhotos,
  loadedPhotos,
  deletingId,
  finalizingId,
  revertingId,
  finalizedData,
  pendingData,
  handleDelete,
  handleFinalize,
  handleRevertToPending,
}) {
  const navigate = useNavigate();

  const getPhoto = async (registrationId) => {
    const result = await ObjectServices.get_photo_base64(registrationId);
    if (result.success) {
      return `data:image/jpeg;base64,${result.data?.file}`;
    }
  };

  // Lazy load photo for a specific registration
  const loadPhoto = async (registrationId) => {
    if (loadingPhotos.has(registrationId)) {
      return;
    }

    let patient;

    if (activeTab === "finalized") {
      patient = finalizedData.filter(
        (patient) => patient.id === registrationId,
      );
    } else {
      patient = pendingData.filter((patient) => patient.id === registrationId);
    }

    const photo = await getPhoto(registrationId);

    if (photo) {
      setLoadedPhotos((prev) => ({
        ...prev,
        [registrationId]: photo,
      }));
    }
  };

  return (
    <div key={item.id} className="border rounded-lg p-4 bg-gray-50">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            {item.first_name} {item.last_name}
            {item.disposition && (
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs font-normal">
                {item.disposition.charAt(0).toUpperCase() +
                  item.disposition.slice(1).toLowerCase()}
              </span>
            )}
          </h3>
          <div className="text-sm text-gray-600 mt-1">
            <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
              Registration Date: {item.reg_date || "Not provided"}
            </p>
            <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
              Submitted: {new Date(item.created_at).toLocaleString()}
            </p>
            {item.finalized_at && (
              <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
                Finalized: {new Date(item.finalized_at).toLocaleString()}
              </p>
            )}
            <p className="text-xs text-gray-500 mt-1">ID: {item.id}</p>
          </div>

          {/* Lazy loaded photo */}
          {loadedPhotos[item.id] && (
            <div className="mt-4 mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Uploaded Photo:
              </p>
              <img
                src={loadedPhotos[item.id]}
                alt="Registration photo"
                className="lg:max-w-xs md:w-3/4 max-h-48 object-contain border rounded"
                onError={(e) => {
                  e.target.style.display = "none";
                }}
              />
            </div>
          )}

          {!loadedPhotos[item.id] && !loadingPhotos.has(item.id) && (
            <button
              onClick={() => loadPhoto(item.id)}
              className="mt-2 text-sm text-blue-600 hover:text-blue-800"
            >
              Load Photo
            </button>
          )}

          {loadingPhotos.has(item.id) && (
            <div className="mt-2 text-sm text-gray-500">Loading photo...</div>
          )}
        </div>
      </div>

      {/* Action Buttons - Horizontal layout with intuitive colors */}
      <div className="flex gap-2 mt-4 flex-wrap">
        <button
          onClick={() => {
            navigate(`/admin-edit/${item.id}`);
          }}
          className="bg-black hover:bg-gray-800 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium flex-1 min-w-[60px]"
        >
          Edit
        </button>

        <button
          onClick={() => handleDelete(item.id, item.first_name, item.last_name)}
          disabled={deletingId === item.id}
          className="bg-red-600 hover:bg-red-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]"
        >
          {deletingId === item.id ? "Deleting..." : "Delete"}
        </button>

        {activeTab === "pending" && (
          <button
            onClick={() =>
              handleFinalize(
                item.id,
                item.first_name,
                item.last_name,
                loadedPhotos[item.id],
              )
            }
            disabled={finalizingId === item.id}
            className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[70px]"
          >
            {finalizingId === item.id ? "Submitting..." : "Submit"}
          </button>
        )}

        {activeTab === "submitted" && (
          <button
            onClick={() =>
              handleRevertToPending(item.id, item.first_name, item.last_name)
            }
            disabled={revertingId === item.id}
            className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[70px]"
          >
            {revertingId === item.id ? "Reverting..." : "Back to Pending"}
          </button>
        )}
      </div>
    </div>
  );
}
