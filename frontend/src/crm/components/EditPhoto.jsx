import { useNavigate } from "react-router-dom";
import React, { useEffect, useState } from "react";
import { compressImage } from "../../utils/compressImage";

export default function EditPhoto({
  saveStatus,
  photoData,
  setPhotoData,
  photoPreview,
  setPhotoPreview,
}) {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [photoUploadStatus, setPhotoUploadStatus] = useState(null);

  useEffect(() => {
    const compressAndSetPreview = async () => {
      if (photoData.file) {
        const compressed = await compressImage(photoData.file, 500);
        setPhotoPreview(compressed);
        setPhotoUploadStatus({
          type: "success",
          message:
            "Photo loaded successfully. Your photo will be attached to the email when you submit the registration.",
        });
      } else {
        setPhotoPreview(null);
        setPhotoUploadStatus(null);
      }
    };

    compressAndSetPreview();
  }, [photoData.file]);

  const handlePhotoChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        alert("Please select an image file");
        return;
      }

      // Validate file size (10MB max before compression)
      if (file.size > 10 * 1024 * 1024) {
        alert("Photo is too large. Please choose an image under 10MB.");
        return;
      }

      setPhotoData({
        name: file.name,
        file: file,
      });

      try {
      } catch (error) {
        setError("Error compressing image:", error);
        alert("Error processing image. Please try again.");
      }
    }
  };

  const goBack = () => {
    navigate("/");
  };

  const removePhoto = () => {
    setPhotoPreview(null);
    setPhotoUploadStatus(null);
    setPhotoData({});

    // Clear both file inputs
    const cameraInput = document.getElementById("photo-camera");
    const uploadInput = document.getElementById("photo-upload");
    if (cameraInput) {
      cameraInput.value = "";
    }
    if (uploadInput) {
      uploadInput.value = "";
    }
  };

  return (
    <>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">
        Edit Registration
      </h1>
      <div className="flex gap-2 mb-4">
        <button
          type="button"
          onClick={() => navigate("/admin-menu")}
          className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
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
          type="button"
          onClick={() => navigate("/admin-dashboard")}
          className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
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
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          Back to Dashboard
        </button>
        <button
          type="button"
          onClick={() => navigate("/")}
          className="inline-flex items-center gap-1 px-3 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
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
      </div>

      {saveStatus && (
        <div
          className={`mb-6 p-4 rounded-md ${
            saveStatus.type === "success"
              ? "bg-green-50 border border-green-200"
              : "bg-red-50 border border-red-200"
          }`}
        >
          <p
            className={
              saveStatus.type === "success" ? "text-green-800" : "text-red-800"
            }
          >
            {saveStatus.message}
          </p>
        </div>
      )}

      {/* Photo Upload Section */}
      <div className="border-b border-gray-200 pb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Client Photo</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Photo Options
            </label>

            {/* Camera Option */}
            <div className="mb-4">
              <label
                htmlFor="photo-camera"
                className="block text-sm font-medium text-gray-600 mb-2"
              >
                📷 Take Photo with Camera
              </label>
              <input
                type="file"
                id="photo-camera"
                accept="image/*"
                capture="environment"
                onChange={handlePhotoChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
              />
            </div>

            {/* Upload Option */}
            <div className="mb-4">
              <label
                htmlFor="photo-upload"
                className="block text-sm font-medium text-gray-600 mb-2"
              >
                📁 Upload Existing Image
              </label>
              <input
                type="file"
                id="photo-upload"
                accept="image/*"
                onChange={handlePhotoChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
              />
            </div>
          </div>

          {photoPreview && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                Photo Preview
              </h3>
              <div className="w-48 h-48 border-2 border-gray-300 rounded-lg overflow-hidden">
                <img
                  src={photoPreview} //photoPreview}
                  alt="Client photo preview"
                  className="w-full h-full object-cover"
                />
              </div>
              <button
                type="button"
                onClick={removePhoto}
                className="mt-2 text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Remove Photo
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
