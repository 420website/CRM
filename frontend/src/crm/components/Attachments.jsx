import { useState, useEffect } from "react";
import { PatientServices } from "../../services/patientServices";
import {
  getPdfPageCount,
  loadImage,
  loadPDF,
  loadWord,
} from "../../utils/loadFile";
import DocumentPreviewModal from "./DocumentPreview";

export default function Attachments({ setActiveTab, currentRegistrationId }) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [documentType, setDocumentType] = useState("");
  const [documentUrl, setDocumentUrl] = useState("");
  const [isLoadingDocument, setIsLoadingDocument] = useState(false);
  const [documentPreview, setDocumentPreview] = useState(null);
  const [documentFile, setDocumentFile] = useState(null);
  const [savedAttachments, setSavedAttachments] = useState([]);
  const [isFullScreenPreview, setIsFullScreenPreview] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20); // Fixed page size for optimal performance
  const [totalPages, setTotalPages] = useState(1);

  // Page navigation functions
  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const getAttachments = async (registrationId) => {
    setLoading(true);
    setError("");

    const result =
      await PatientServices.get_attachments_by_patient(registrationId);

    if (result.success) {
      setSavedAttachments(result.data || []);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const saveAttachment = async () => {
    setLoading(true);
    setError("");

    // Check if patient form has been submitted (registration ID exists)
    if (!currentRegistrationId) {
      alert(
        "Please complete and save the Client tab form first before adding tests.",
      );
      setActiveTab("client");
      return;
    }

    if (!documentType) {
      alert("Please select a document type");
      return;
    }

    if (!documentFile && !documentUrl.trim()) {
      alert("Please upload a file or provide a URL");
      return;
    }

    // Create attachment object - use base64 for storage, blob for display
    const attachmentData = {
      type: documentType,
      filename: documentPreview.filename,
      url: documentPreview.base64 || documentPreview.url, // Use base64 for storage
      document_type: documentPreview.type,
      is_local: documentPreview.is_local || false,
      original_url: documentPreview.base64 || documentPreview.url, // Backup of original URL
    };

    const result = await PatientServices.create_attachment(
      currentRegistrationId,
      attachmentData,
    );

    if (result.success) {
      await getAttachments(currentRegistrationId);

      clearDocument();
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const deleteAttachment = async (attachmentId) => {
    if (!window.confirm(`Are you sure you want to remove this attachment?`)) {
      return;
    }

    setLoading(true);
    setError("");
    const result = await PatientServices.delete_attachment_by_id(
      currentRegistrationId,
      attachmentId,
    );

    if (result.success) {
      await getAttachments(currentRegistrationId);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting dispositions.");
      } else {
        setError("Error getting dispositions. Please try again.");
      }
    }
    setLoading(false);
  };

  const viewAttachment = async (attachment) => {
    // Clear current state first
    setDocumentFile(null);
    setDocumentUrl("");
    setDocumentPreview(null);
    setDocumentType(attachment.type);
    console.log(attachment);

    // Clear file input
    const fileInput = document.getElementById("documentFile");
    if (fileInput) fileInput.value = "";

    if (attachment.document_type === "pdf") {
      const totalPages = await getPdfPageCount(attachment.url);
      setTotalPages(totalPages);
      setCurrentPage(1);
    }

    // Use a setTimeout to ensure state is cleared before setting new preview
    setTimeout(() => {
      // Ensure proper URL format for images
      let previewUrl = attachment.url;

      // For images, ensure they have the proper base64 data URI format
      if (
        attachment.document_type === "image" &&
        previewUrl &&
        !previewUrl.startsWith("data:image/")
      ) {
        // If it's a raw base64 string, add the proper prefix
        if (!previewUrl.startsWith("data:")) {
          previewUrl = `data:image/jpeg;base64,${previewUrl}`;
        }
      }

      // Set the document preview with the exact same structure as upload
      setDocumentPreview({
        id: attachment.id,
        type: attachment.document_type,
        url: previewUrl,
        filename: attachment.filename,
        is_local: attachment.is_local || false,
      });
    }, 50);
  };

  const clearDocument = () => {
    // Clean up object URL if it's a local file
    if (documentPreview && documentPreview.is_local && documentPreview.url) {
      URL.revokeObjectURL(documentPreview.url);
    }

    setDocumentFile(null);
    setDocumentUrl("");
    setDocumentPreview(null);
    setDocumentType("");
    setIsFullScreenPreview(false); // Also close full-screen preview

    // Clear file input
    const fileInput = document.getElementById("documentFile");
    if (fileInput) {
      fileInput.value = "";
    }
  };

  const openFullScreenPreview = () => {
    console.log("foo");
    if (
      documentPreview &&
      (documentPreview.type === "pdf" || documentPreview.type === "image")
    ) {
      console.log("bar");
      setIsFullScreenPreview(true);
    }
  };

  const closeFullScreenPreview = () => {
    console.log("top");
    setIsFullScreenPreview(false);
  };

  const loadDocument = (
    file,
    setDocumentPreview,
    setCurrentPage,
    setTotalPages,
  ) => {
    if (file.type.startsWith("image/")) {
      loadImage(file, setDocumentPreview);
    } else if (file.type === "application/pdf") {
      loadPDF(file, setDocumentPreview, setCurrentPage, setTotalPages);
    } else if (
      file.type ===
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
      file.type === "application/msword"
    ) {
      loadWord(file, setDocumentPreview);
    } else {
      console.warn("Unsupported file type:", file.type);
    }
  };

  // Document handling functions
  const handleDocumentFileChange = async (e) => {
    const file = e.target.files[0];

    if (file) {
      // Validate file type
      const allowedTypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/jpg",
        "image/png",
      ];

      if (!allowedTypes.includes(file.type)) {
        alert("Please select a valid file type (PDF, DOC, DOCX, JPG, PNG)");
        e.target.value = "";
        return;
      }

      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert("File is too large. Please choose a file under 10MB.");
        e.target.value = "";
        return;
      }

      loadDocument(file, setDocumentPreview, setCurrentPage, setTotalPages);
      setDocumentFile(file);
    }
  };

  const handleLoadUrl = async () => {
    if (!documentUrl.trim()) {
      alert("Please enter a valid URL");
      return;
    }

    setIsLoadingDocument(true);

    try {
      // Basic URL validation
      const url = new URL(documentUrl);

      // Check if it's a PDF or image URL based on extension
      const extension = url.pathname.split(".").pop().toLowerCase();

      if (["pdf"].includes(extension)) {
        setDocumentPreview({
          type: "pdf",
          url: documentUrl,
          filename: url.pathname.split("/").pop(),
          is_local: false,
        });
      } else if (["jpg", "jpeg", "png"].includes(extension)) {
        // For image URLs, need to handle them differently since they might not load properly
        // For now, just create a preview that links to the original URL
        setDocumentPreview({
          type: "image",
          url: documentUrl,
          filename: url.pathname.split("/").pop(),
        });
      } else {
        setDocumentPreview({
          type: "link",
          url: documentUrl,
          filename: url.pathname.split("/").pop() || "Document",
        });
      }
    } catch (error) {
      alert("Please enter a valid URL");
    } finally {
      setIsLoadingDocument(false);
    }
  };

  useEffect(() => {
    if (currentRegistrationId) {
      getAttachments(currentRegistrationId);
    }
  }, [currentRegistrationId]);

  return (
    <div className="tab-content">
      <div className="space-y-6">
        {!currentRegistrationId && (
          <div className="border-2 border-orange-200 bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-orange-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-orange-800">
                  Client Registration Required
                </h3>
                <div className="mt-2 text-sm text-orange-700">
                  <p>
                    Please complete and save the Client tab form first before
                    adding tests. This will create a registration record that
                    tests can be associated with.
                  </p>
                </div>
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={() => setActiveTab("client")}
                    className="bg-orange-100 text-orange-800 px-4 py-2 rounded-md hover:bg-orange-200 transition-colors"
                  >
                    Go to Client Tab
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Add New Document
          </h2>

          {/* Document Type Selection */}
          <div className="mb-6">
            <label
              htmlFor="documentType"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Document Type
            </label>
            <select
              id="documentType"
              name="documentType"
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              style={{ maxHeight: "150px", overflowY: "auto" }}
              size="1"
            >
              <option value="">Select Document Type</option>
              <option value="consultation-report">Consultation Report</option>
              <option value="treatment-consent">Treatment Consent</option>
              <option value="hcv-prescription">HCV Prescription</option>
            </select>
          </div>

          {/* File Upload Options */}
          <div className="mb-6">
            <h3 className="text-md font-medium text-gray-900 mb-3">
              Upload Methods
            </h3>

            {/* URL Input */}
            <div className="mb-4">
              <label
                htmlFor="documentUrl"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                📎 Paste Document URL
              </label>
              <div className="flex gap-2">
                <input
                  type="url"
                  id="documentUrl"
                  name="documentUrl"
                  value={documentUrl}
                  onChange={(e) => setDocumentUrl(e.target.value)}
                  placeholder="https://example.com/document.pdf"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
                />
                <button
                  type="button"
                  onClick={handleLoadUrl}
                  disabled={isLoadingDocument}
                  className="px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                >
                  {isLoadingDocument ? "Loading..." : "Load URL"}
                </button>
              </div>
            </div>

            {/* File Upload */}
            <div className="mb-4">
              <label
                htmlFor="documentFile"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                📁 Upload Document File
              </label>
              <input
                type="file"
                id="documentFile"
                name="documentFile"
                onChange={handleDocumentFileChange}
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-800"
              />
              <p className="mt-1 text-xs text-gray-500">
                Supported formats: PDF, DOC, DOCX, JPG, PNG (Max 10MB)
              </p>
            </div>
          </div>

          {/* Document Preview */}
          <div className="mb-6">
            <h3 className="text-md font-medium text-gray-900 mb-3">
              Document Preview
            </h3>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center min-h-96">
              {documentPreview ? (
                <div className="space-y-4">
                  {documentPreview.type === "image" && (
                    <div
                      className="cursor-pointer transition-transform hover:scale-105"
                      onClick={openFullScreenPreview}
                      key={
                        documentPreview.filename +
                        documentPreview.url?.substring(0, 20)
                      } // Force re-render
                    >
                      <img
                        src={documentPreview.url}
                        alt="Document preview"
                        className="w-full h-full object-contain border-2 border-gray-300 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                        style={{
                          minHeight: "300px",
                          maxHeight: "350px",
                        }}
                        key={documentPreview.url?.substring(0, 50)} // Force img re-render
                      />
                    </div>
                  )}
                  {documentPreview.type === "pdf" && (
                    <div className="space-y-4">
                      {/* PDF Preview */}
                      <div
                        className="border-2 border-gray-300 rounded-lg overflow-hidden shadow-md"
                        style={{ height: "600px" }}
                      >
                        <iframe
                          key={`pdf-preview-${currentPage}-${documentPreview.filename}`}
                          src={`${documentPreview.url}#page=${currentPage}&view=FitV&zoom=85&toolbar=0`}
                          className="w-full h-full"
                          title="PDF Preview"
                          style={{ border: "none" }}
                        />
                      </div>

                      {/* Navigation Controls - Clean Layout */}
                      <div className="bg-gray-50 border rounded-lg p-4">
                        <div className="flex items-center justify-between max-w-md mx-auto">
                          <button
                            type="button"
                            onClick={prevPage}
                            disabled={currentPage <= 1}
                            className="px-4 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                          >
                            ← Prev
                          </button>

                          <div className="flex items-center space-x-2">
                            <span className="text-sm text-gray-600">Page</span>
                            <input
                              type="number"
                              value={currentPage}
                              onChange={(e) => {
                                const page = parseInt(e.target.value);
                                if (page >= 1 && page <= totalPages) {
                                  setCurrentPage(page);
                                }
                              }}
                              min="1"
                              max={totalPages}
                              className="w-16 px-2 py-1 border border-gray-300 rounded text-center text-sm"
                            />
                            <span className="text-sm text-gray-600">
                              of {totalPages}
                            </span>
                          </div>

                          <button
                            type="button"
                            onClick={nextPage}
                            disabled={currentPage >= totalPages}
                            className="px-4 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                          >
                            Next →
                          </button>
                        </div>
                      </div>

                      {/* Full Screen Button */}
                      <div className="text-center mt-4">
                        <button
                          type="button"
                          onClick={openFullScreenPreview}
                          className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 text-sm"
                        >
                          📄 View Full Screen
                        </button>
                      </div>
                    </div>
                  )}
                  {documentPreview.type === "document" && (
                    <div className="text-gray-600">
                      <svg
                        className="mx-auto h-12 w-12 mb-2"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <p className="text-sm">Document ready for upload</p>
                    </div>
                  )}
                  {documentPreview.type === "link" && (
                    <div className="text-blue-600">
                      <svg
                        className="mx-auto h-12 w-12 mb-2"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <p className="text-sm">External link loaded</p>
                      <a
                        href={documentPreview.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 underline"
                      >
                        Open in new tab
                      </a>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-gray-400">
                  <svg
                    className="mx-auto h-12 w-12 mb-4"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <p className="text-sm">No document loaded</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Upload a file or paste a URL to preview
                  </p>
                </div>
              )}
            </div>
            {/* Click instruction text - positioned OUTSIDE the preview frame */}
            {documentPreview && (
              <p className="text-center text-xs text-gray-500 mt-3">
                Click image to see full screen
              </p>
            )}
          </div>

          {/* Document Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={clearDocument}
              className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
            >
              Clear Document
            </button>
            <button
              type="button"
              onClick={saveAttachment}
              className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-semibold"
            >
              Save Attachment
            </button>
          </div>

          {/* Saved Attachments List */}
          {savedAttachments.length > 0 && (
            <div className="mt-8 border-t pt-6">
              <h3 className="text-md font-medium text-gray-900 mb-4">
                Saved Attachments ({savedAttachments.length})
              </h3>
              <div className="space-y-3">
                {savedAttachments.map((attachment) => (
                  <div
                    key={attachment.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        {attachment.document_type === "pdf" ? (
                          <svg
                            className="h-6 w-6 mr-3 text-red-600"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                              clipRule="evenodd"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="h-6 w-6 mr-3 text-green-600"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {attachment.type}
                          </p>
                          <p className="text-xs text-gray-500">
                            {attachment.filename}
                          </p>
                          <p className="text-xs text-gray-400">
                            Saved: {attachment.created_at.split("T")[0]},{" "}
                            {new Date(attachment.created_at).toLocaleTimeString(
                              "en-US",
                              {
                                timeZone: "America/New_York",
                                hour12: true,
                              },
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => viewAttachment(attachment)}
                          className="bg-black text-white px-3 py-1 rounded text-xs hover:bg-gray-800 transition-colors"
                        >
                          View
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteAttachment(attachment.id)}
                          className="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700 transition-colors"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div>
        {isFullScreenPreview &&
          documentPreview &&
          (documentPreview.type === "pdf" ||
            documentPreview.type === "image") && (
            <DocumentPreviewModal
              documentPreview={documentPreview}
              totalPages={totalPages}
              closeFullScreenPreview={closeFullScreenPreview}
            />
          )}
      </div>
    </div>
  );
}
