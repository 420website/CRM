import { useEffect, useState } from "react";
import { compressImageToBlob } from "../../utils/compressImage";
import toast from "react-hot-toast";
import { Trash } from "lucide-react";
import { Image } from "lucide-react";
import { Upload } from "lucide-react";
import { Video } from "lucide-react";
import { ImageOff } from "lucide-react";
import { ObjectServices } from "../../services/objectService";
import ConfirmModal from "./ConfirmModal";
import { useDashboard } from "../../context/DashboardContext";
import { useNavigate } from "react-router-dom";
import { useZoom } from "../../context/ZoomContext";

export default function EditPhoto({ registrationId, formData }) {
  const navigate = useNavigate();
  const { setReturnUrl } = useZoom();

  const { getDashboardRegistrations, getDashboardActivities } = useDashboard();
  const [showingPhoto, setShowingPhoto] = useState(false);
  const [showConfirm, setShowConfirm] = useState("");
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoData, setPhotoData] = useState({});

  const getClientPhoto = async () => {
    const result = await ObjectServices.get_photo_raw(registrationId);

    if (result.success) {
      const blob = new Blob([result.data], { type: "image/jpeg" });
      const url = URL.createObjectURL(blob);
      setPhotoPreview(url);
      setPhotoData({
        name: result.headers["file-name"],
      });
    } else {
      if (result.status === 404) {
        return;
      } else if (result.status === 400 || result.status === 409) {
        toast.error(result.message || "Failed to fetch client photo.");
      } else {
        toast.error(result.message || "Failed to fetch client photo.");
      }
    }
  };

  useEffect(() => {
    if (registrationId) {
      getClientPhoto();
    }
  }, [registrationId]);

  const uploadPhoto = async (e) => {
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

      setPhotoData({
        name: newFileName,
        file: compressedImage,
      });
      setPhotoPreview(URL.createObjectURL(compressedImage));

      await handleUploadPhoto(registrationId, newFileName, compressedImage);
    }
  };

  const handleUploadPhoto = async (id, name, file) => {
    const photoRes = await ObjectServices.upload_photo(id, name, file);

    if (photoRes.success) {
      getDashboardRegistrations();
      getDashboardActivities();
      toast.success("Photo saved successfully");
    } else {
      toast.error(result.message || "Error saving photo.");
    }
    setShowConfirm("");
  };

  const removePhoto = () => {
    // Only mark as changed if there was actually a photo
    if (photoPreview || photoData.name) {
      setPhotoPreview(null);
      setPhotoData({});

      const uploadInput = document.getElementById("photo-upload");
      if (uploadInput) {
        uploadInput.value = "";
      }
    }
  };

  const handleDeletePhoto = async (id) => {
    const deleteRes = await ObjectServices.delete_photo(id);

    if (deleteRes.success) {
      getDashboardRegistrations();
      getDashboardActivities();
      toast.success("Photo deleted successfully");
    } else {
      toast.error(deleteRes.message || "Error deleting photo.");
    }

    removePhoto();
    setShowConfirm("");
  };

  const handleClickVideo = async () => {
    setReturnUrl(`/admin-edit/${registrationId}`);
    navigate(`/preview/${registrationId}`);
  };

  return (
    <div id="editPhoto" className="mb-0">
      {showConfirm === "delete" && (
        <ConfirmModal
          message={"Confirm to delete photo"}
          subMessage={"This action cannot be undone"}
          confirm={() => handleDeletePhoto(registrationId)}
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
      {/* Photo Upload Section */}
      <div className="border-b border-gray-200 pb-2 flex flex-col">
        <div className="flex gap-4 items-center">
          <h2 className="text-lg font-medium text-gray-900">Client Profile</h2>
          <div className="flex items-center gap-4">
            <div className="flex gap-2 items-center">
              <input
                type="file"
                id="photo-upload"
                accept="image/*"
                onChange={uploadPhoto}
                className="hidden"
              />
              {photoPreview ? (
                showingPhoto ? (
                  <button type="button" onClick={() => setShowingPhoto(false)}>
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
              <button type="button" onClick={handleClickVideo}>
                <Video className="w-4 h-4" />
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
        <div className="space-y-4">
          <p className="mt-2 text-sm text-gray-500">
            File: {formData.file_id || "NA"} ID: {formData.id || "Unknown"}
          </p>
        </div>
      </div>
    </div>
  );
}
