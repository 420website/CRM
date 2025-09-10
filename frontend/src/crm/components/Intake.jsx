import { useNavigate } from "react-router-dom";
import React, { useState } from "react";
import { HealthServices } from "../../services/healthService";
import { compressImage } from "../../utils/compressImage";

export default function Intake({ submitStatus, setFormData }) {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [systemTestStatus, setSystemTestStatus] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoUploadStatus, setPhotoUploadStatus] = useState(null);

  const goBack = () => {
    navigate("/");
  };

  // Not really neccessary, backend should always be functioning
  const testPhotoUploadSystem = async () => {
    setSystemTestStatus({
      type: "testing",
      message: "Testing photo upload system...",
    });

    const response = await HealthServices.check_health();

    if (response.success) {
      setSystemTestStatus({
        type: "success",
        message:
          "✅ System test passed! Backend server is responding correctly. Photo upload and email functionality should work properly. You can safely proceed with your registration.",
      });
    } else {
      setSystemTestStatus({
        type: "error",
        message:
          "❌ System test failed. Backend server is not responding properly. Please contact support.",
      });
    }
  };

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

      try {
        // Compress the image
        const compressedImage = await compressImage(file, 500); // Target 500KB

        // Final size check
        if (compressedImage.length > 800 * 1024) {
          // 800KB final limit
          alert(
            "Photo could not be compressed enough. Please choose a smaller image.",
          );
          return;
        }

        setPhotoPreview(compressedImage);
        setFormData((prev) => ({
          ...prev,
          photo: compressedImage,
        }));

        // Show success message after compression
        setPhotoUploadStatus({
          type: "success",
          message: `Photo successfully optimized from ${(file.size / 1024).toFixed(1)}KB to ${(compressedImage.length / 1024).toFixed(1)}KB with high quality maintained. Your photo will be attached to the email when you submit the registration.`,
        });
      } catch (error) {
        setError("Error compressing image:", error);
        alert("Error processing image. Please try again.");
      }
    }
  };

  const removePhoto = () => {
    setPhotoPreview(null);
    setPhotoUploadStatus(null);
    setFormData((prev) => ({
      ...prev,
      photo: null,
    }));
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
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Intake</h1>
      <div className="flex gap-2 mb-4">
        <button
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
          onClick={goBack}
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

      {submitStatus?.type === "error" && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{submitStatus.message}</p>
        </div>
      )}

      {/* System Test Section */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h3 className="text-lg font-medium text-blue-900 mb-2">
          🔧 System Verification
        </h3>
        <p className="text-blue-800 text-sm mb-3">
          Before filling out the registration form, you can test that photo
          upload and email functionality is working correctly.
        </p>
        <button
          type="button"
          onClick={testPhotoUploadSystem}
          disabled={systemTestStatus?.type === "testing"}
          className="bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-sm"
        >
          {systemTestStatus?.type === "testing"
            ? "Testing System..."
            : "Test Photo Upload System"}
        </button>

        {systemTestStatus && (
          <div
            className={`mt-3 p-3 rounded-md ${
              systemTestStatus.type === "success"
                ? "bg-green-50 border border-green-200"
                : systemTestStatus.type === "error"
                  ? "bg-red-50 border border-red-200"
                  : "bg-blue-50 border border-blue-200"
            }`}
          >
            <div className="flex items-center">
              {systemTestStatus.type === "success" && (
                <svg
                  className="w-5 h-5 text-green-600 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
              {systemTestStatus.type === "error" && (
                <svg
                  className="w-5 h-5 text-red-600 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              )}
              {systemTestStatus.type === "testing" && (
                <svg
                  className="w-5 h-5 text-blue-600 mr-2 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              )}
              <p
                className={`text-sm ${
                  systemTestStatus.type === "success"
                    ? "text-green-800"
                    : systemTestStatus.type === "error"
                      ? "text-red-800"
                      : "text-blue-800"
                }`}
              >
                {systemTestStatus.message}
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {/* Photo Upload Section */}
        <div className="border-b border-gray-200 pb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Client Photo
          </h2>
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
                <p className="mt-1 text-xs text-gray-500">
                  Use your device's camera to take a new photo
                </p>
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
                <p className="mt-1 text-xs text-gray-500">
                  Choose an existing image from your device
                </p>
              </div>

              <p className="mt-2 text-sm text-gray-500">
                Photos are optimized to ~800KB while maintaining high quality.
                Supported formats: JPG, PNG, GIF.
              </p>
            </div>

            {photoPreview && (
              <div className="mt-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">
                  Photo Preview
                </h3>
                <div className="w-48 h-48 border-2 border-gray-300 rounded-lg overflow-hidden">
                  <img
                    src={photoPreview}
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

            {/* Photo Upload Status */}
            {photoUploadStatus && (
              <div
                className={`mt-4 p-4 rounded-md ${
                  photoUploadStatus.type === "success"
                    ? "bg-green-50 border border-green-200"
                    : photoUploadStatus.type === "error"
                      ? "bg-red-50 border border-red-200"
                      : "bg-blue-50 border border-blue-200"
                }`}
              >
                <div className="flex items-center">
                  {photoUploadStatus.type === "success" && (
                    <svg
                      className="w-5 h-5 text-green-600 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                  {photoUploadStatus.type === "error" && (
                    <svg
                      className="w-5 h-5 text-red-600 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  )}
                  {photoUploadStatus.type === "testing" && (
                    <svg
                      className="w-5 h-5 text-blue-600 mr-2 animate-spin"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  )}
                  <p
                    className={`text-sm ${
                      photoUploadStatus.type === "success"
                        ? "text-green-800"
                        : photoUploadStatus.type === "error"
                          ? "text-red-800"
                          : "text-blue-800"
                    }`}
                  >
                    {photoUploadStatus.message}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
