import { useNavigate } from "react-router-dom";
import { ObjectServices } from "../../services/objectService";
import { useCallback, useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";

export function RegistrationItems({
  activeTab,
  deletingId,
  finalizingId,
  revertingId,
  finalizedData,
  pendingData,
  handleSave,
  handleDelete,
  handleFinalize,
  handleRevertToPending,
  filteredData,
}) {
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

  const showPhoto = async (registrationId, index) => {
    if (loadedPhotos[registrationId]) {
      const isShowing = showingPhotos.some(
        ([id, idx]) => id === registrationId && idx === index,
      );

      if (!isShowing) {
        setShowingPhotos([...showingPhotos, [registrationId, index]]);
        return;
      }
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
      setShowingPhotos([...showingPhotos, [registrationId, index]]);
    }
  };

  const hidePhoto = async (registrationId, index) => {
    setShowingPhotos((prev) =>
      prev.filter(([id, idx]) => !(id === registrationId && idx === index)),
    );
  };

  const renderRegistrationItem = useCallback(
    (item, index) => (
      <RegistrationItem
        key={item.id}
        index={index}
        activeTab={activeTab}
        item={item}
        loadingPhotos={loadingPhotos}
        loadedPhotos={loadedPhotos}
        deletingId={deletingId}
        finalizingId={finalizingId}
        revertingId={revertingId}
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
      deletingId,
      finalizingId,
      activeTab,
      showingPhotos,
    ],
  );

  return <div>{filteredData.map(renderRegistrationItem)}</div>;
}

export default function RegistrationItem({
  index,
  activeTab,
  item,
  loadingPhotos,
  loadedPhotos,
  deletingId,
  finalizingId,
  revertingId,
  handleDelete,
  handleSave,
  handleFinalize,
  handleRevertToPending,
  showPhoto,
  hidePhoto,
  showingPhotos,
}) {
  const navigate = useNavigate();
  const nameRef = useRef(null);
  const [nameOnOneLine, setNameOnOneLine] = useState(true);

  const isShowing = showingPhotos.some(
    ([id, idx]) => id === item.id && idx === index,
  );

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
    <div key={item.id} className="border rounded-lg p-4 bg-gray-50 mb-2">
      <div className="flex justify-between items-start">
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start gap-2 min-w-0">
            <h3
              ref={nameRef}
              className="text-lg font-semibold text-gray-900 min-w-0 break-words"
            >
              {nameOnOneLine ? (
                <>
                  <span>{item.first_name}</span> <span>{item.last_name}</span>
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
                new Date(item.created_at).toLocaleDateString("en-CA") ||
                "Not provided"
              }`}
            </p>
            <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
              Submitted: {new Date(item.created_at).toLocaleString()}
            </p>
            {(item.status === "finalized" || item.status === "saved") &&
              item.finalized_at && (
                <p style={{ whiteSpace: "nowrap", fontSize: "14px" }}>
                  Finalized: {new Date(item.finalized_at).toLocaleString()}
                </p>
              )}
          </div>

          {!isShowing && (
            <button
              onClick={() => showPhoto(item.id, index)}
              className="flex justify-start mt-2 mb-2 text-sm text-blue-600 hover:text-blue-800"
            >
              Show Photo
            </button>
          )}

          {isShowing && (
            <button
              onClick={() => hidePhoto(item.id, index)}
              className="flex justify-start mt-2 mb-2 text-sm text-blue-600 hover:text-blue-800"
            >
              Hide Photo
            </button>
          )}

          {/* Photo and buttons*/}
          <div
            className={`flex gap-2 justify-between ${isShowing ? "flex-row" : "flex-col"}`}
          >
            {/* Lazy loaded photo */}
            {isShowing && (
              <div className="flex-grow">
                <img
                  src={loadedPhotos[item.id]}
                  alt="Registration photo"
                  className="w-64 h-48 object-cover border rounded"
                  onError={(e) => {
                    e.target.style.display = "none";
                  }}
                />
              </div>
            )}

            {loadingPhotos.has(item.id) && (
              <div className="mt-2 text-sm text-gray-500">Loading photo...</div>
            )}

            {/* Action Buttons - Horizontal layout with intuitive colors */}
            <div
              className={`flex gap-2  ${isShowing ? "flex-col" : "flex-row"}`}
            >
              <button
                onClick={() => handleDelete(item.id)}
                disabled={deletingId === item.id}
                className={`bg-red-600 hover:bg-red-700 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]`}
              >
                {deletingId === item.id ? "Deleting..." : "Delete"}
              </button>
              <button
                onClick={() => {
                  navigate(`/admin-edit/${item.id}`);
                }}
                className={`bg-black hover:bg-gray-800 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium flex-1 min-w-[60px]`}
              >
                Edit
              </button>

              {activeTab === "pending" && (
                <>
                  <button
                    onClick={() => {
                      hidePhoto(item.id, index);
                      handleSave(item.id);
                    }}
                    disabled={finalizingId === item.id}
                    className={`bg-black hover:bg-gray-800 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]`}
                  >
                    {finalizingId === item.id ? "Saving..." : "Save"}
                  </button>
                  <button
                    onClick={() => {
                      hidePhoto(item.id, index);
                      handleFinalize(item.id);
                    }}
                    disabled={finalizingId === item.id}
                    className={`bg-green-600 hover:bg-green-700 text-white ${isShowing ? "py-1 px-2" : "py-2 px-3"} rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]`}
                  >
                    {finalizingId === item.id ? "Submitting..." : "Submit"}
                  </button>
                </>
              )}

              {activeTab === "submitted" && (
                <button
                  onClick={() => handleRevertToPending(item.id)}
                  disabled={revertingId === item.id}
                  className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]"
                >
                  {revertingId === item.id ? "Reverting..." : "Back to Pending"}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
