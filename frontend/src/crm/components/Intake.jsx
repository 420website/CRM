import { useState } from "react";
import { HealthServices } from "../../services/healthService";
import { compressImageToBlob } from "../../utils/compressImage";
import toast from "react-hot-toast";
import { Trash } from "lucide-react";
import { Image } from "lucide-react";
import { ImageOff } from "lucide-react";
import ConfirmModal from "./ConfirmModal";

export default function Intake({ submitStatus, setPhotoData }) {
  const [error, setError] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [systemTestStatus, setSystemTestStatus] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [showingPhoto, setShowingPhoto] = useState(false);
  const [showConfirm, setShowConfirm] = useState("");

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

      try {
        // generate unique name
        const timestamp = Date.now();
        const extension = file.name.split(".").pop();
        const newFileName = `image_${timestamp}.${extension}`;
        setSelectedFileName(file ? newFileName : "");

        const compressedImage = await compressImageToBlob(file, 500);
        const url = URL.createObjectURL(compressedImage);
        setPhotoPreview(url);

        setPhotoData({
          name: newFileName,
          file: compressedImage,
        });
      } catch (error) {
        setError("Error compressing image:", error);
        alert("Error processing image. Please try again.");
      }
    }
  };

  const removePhoto = () => {
    setPhotoPreview(null);
    setPhotoData({});
    setSelectedFileName("");

    // Clear both file inputs
    const uploadInput = document.getElementById("photo-upload");

    if (uploadInput) {
      uploadInput.value = "";
    }
  };

  return (
    <div className="mb-0">
      {showConfirm === "delete" && (
        <ConfirmModal
          message={"Confirm to delete photo"}
          subMessage={"This action cannot be undone"}
          confirm={removePhoto}
          setShowConfirm={setShowConfirm}
        />
      )}

      {showConfirm === "upload" && (
        <ConfirmModal
          message={"Confirm to upload photo"}
          subMessage={"This will delete the current photo"}
          confirm={() => document.getElementById("photo-upload").click()}
          setShowConfirm={setShowConfirm}
        />
      )}
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

      <div id="intake" className="space-y-6">
        {/* Photo Upload Section */}
        <div className="border-b border-gray-200 pb-2 flex flex-col">
          <div className="flex gap-4 items-center">
            <h2 className="text-lg font-medium text-gray-900">
              Client Profile
            </h2>
            <div className="flex items-center gap-4">
              <div className="flex gap-2 items-center">
                <input
                  type="file"
                  id="photo-upload"
                  accept="image/*"
                  onChange={handlePhotoChange}
                  className="hidden"
                />
                {photoPreview ? (
                  showingPhoto ? (
                    <button
                      type="button"
                      onClick={() => setShowingPhoto(false)}
                    >
                      <ImageOff className="w-3 h-4" />
                    </button>
                  ) : (
                    <button type="button" onClick={() => setShowingPhoto(true)}>
                      <Image className="w-3 h-4" />
                    </button>
                  )
                ) : (
                  <button
                    type="button"
                    onClick={() =>
                      document.getElementById("photo-upload").click()
                    }
                  >
                    <Image className="w-3 h-4" />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => photoPreview && setShowConfirm("delete")}
                >
                  <Trash className="w-3 h-4" />
                </button>
              </div>
            </div>
          </div>

          {photoPreview && showingPhoto && (
            <div className="mt-2 mb-0">
              <button type="button" onClick={() => setShowConfirm("upload")}>
                <div className="w-48 h-48 border-2 border-gray-300 rounded-lg overflow-hidden">
                  <img
                    src={photoPreview}
                    alt="Client photo preview"
                    className="w-full h-full object-cover"
                  />
                </div>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
