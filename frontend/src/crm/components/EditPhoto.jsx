import { useState } from "react";
import { compressImageToBlob } from "../../utils/compressImage";
import toast from "react-hot-toast";
import { Trash } from "lucide-react";
import { Image } from "lucide-react";
import { ImageOff } from "lucide-react";

export default function EditPhoto({
  formData,
  photoData,
  setPhotoData,
  photoPreview,
  setPhotoPreview,
  setPhotoChanged,
}) {
  const [showingPhoto, setShowingPhoto] = useState(false);

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

      setPhotoData({
        name: newFileName,
        file: compressedImage,
      });
      setPhotoChanged(true);
      setPhotoPreview(URL.createObjectURL(compressedImage));
    }
  };

  const removePhoto = () => {
    // Only mark as changed if there was actually a photo
    if (photoPreview || photoData.name) {
      setPhotoPreview(null);
      setPhotoData({});
      setPhotoChanged(true);

      const uploadInput = document.getElementById("photo-upload");
      if (uploadInput) {
        uploadInput.value = "";
      }
    }
  };

  return (
    <div id="editPhoto" className="mb-0">
      {/* Photo Upload Section */}
      <div className="border-b border-gray-200 pb-2">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Client Profile
        </h2>
        <div className="space-y-4">
          <div className="p-0 mb-0">
            {/* Upload Option */}
            <div className="mb-2">
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
            <p className="mt-0 text-sm text-gray-500">
              Photos are optimized to ~800KB while maintaining high quality.
              Supported formats: JPG, PNG, GIF.
            </p>
          </div>

          {photoPreview && (
            <>
              <div className="flex items-center gap-4 mt-2 mb-0">
                <h3 className="text-sm font-medium text-gray-900">
                  Photo Preview
                </h3>

                <div className="flex gap-2">
                  {showingPhoto ? (
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
                  )}
                  <button type="button" onClick={removePhoto}>
                    <Trash className="w-3 h-4" />
                  </button>
                </div>
              </div>
              {showingPhoto && (
                <div className="mt-2 mb-0">
                  <div className="w-48 h-48 border-2 border-gray-300 rounded-lg overflow-hidden">
                    <img
                      src={photoPreview}
                      alt="Client photo preview"
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              )}
            </>
          )}

          <p className="mt-2 text-sm text-gray-500">
            File: {formData.file_id || "NA"} ID: {formData.id || "Unknown"}
          </p>
        </div>
      </div>
    </div>
  );
}
