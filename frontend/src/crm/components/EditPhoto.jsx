import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { compressImageToBlob } from "../../utils/compressImage";
import toast from "react-hot-toast";

export default function EditPhoto({
  saveStatus,
  photoData,
  setPhotoData,
  photoPreview,
  setPhotoPreview,
  setPhotoChanged,
}) {
  const navigate = useNavigate();
  const [photoUploadStatus, setPhotoUploadStatus] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState(photoData.name);

  useEffect(() => {
    const compressAndSetPreview = async () => {
      if (photoData.file) {
        setPhotoPreview(URL.createObjectURL(photoData.file));
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
        toast.error("Please select an image file");
        e.target.value = null;
        return;
      }

      // Validate file size (10MB max before compression)
      if (file.size > 10 * 1024 * 1024) {
        toast.error("Photo is too large. Please choose an image under 10MB.");
        e.target.value = null;
        return;
      }
      // Compress for viewing
      const compressedImage = await compressImageToBlob(file, 500);

      // generate unique name
      const timestamp = Date.now();
      const extension = file.name.split(".").pop();
      const newFileName = `image_${timestamp}.${extension}`;

      setSelectedFileName(file ? newFileName : "");
      setPhotoData({
        name: newFileName,
        file: compressedImage,
      });
      setPhotoChanged(true);
    }
  };

  const removePhoto = () => {
    setPhotoPreview(null);
    setPhotoUploadStatus(null);
    setPhotoData({});
    setPhotoChanged(true);
    setSelectedFileName("");

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
    <div id="editPhoto" className="mb-0">
      <h1 className="text-2xl font-bold text-gray-900">Edit Registration</h1>
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
            {/* Upload Option */}
            <div className="mb-4">
              <div>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    className="bg-black text-white text-sm font-semibold py-2 px-4 rounded-md hover:bg-gray-800"
                    onClick={() =>
                      document.getElementById("photo-upload").click()
                    }
                  >
                    Upload Photo
                  </button>

                  <span className="text-sm text-gray-600 truncate max-w-[200px]">
                    {photoData.name || "No file chosen"}
                  </span>

                  <input
                    type="file"
                    id="photo-upload"
                    accept="image/*"
                    onChange={handlePhotoChange}
                    className="hidden"
                  />
                </div>
              </div>
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
        </div>
      </div>
    </div>
  );
}
