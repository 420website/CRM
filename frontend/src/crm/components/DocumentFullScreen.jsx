import { useEffect, useRef, useState } from "react";
import { ShareLinkServices } from "../../services/shareLinkService";
import { Document, Page, pdfjs } from "react-pdf";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

export default function DocumentFullScreen({
  documentPreview,
  totalPages,
  closeFullScreenPreview,
}) {
  // Sharing functionality state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [shareUrl, setShareUrl] = useState("");
  const [isSharing, setIsSharing] = useState(false);
  const [shareStatus, setShareStatus] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pdfScale, setPdfScale] = useState(1.0);
  const [pdfError, setPdfError] = useState(null);
  const [containerWidth, setContainerWidth] = useState(0);
  const [hasSetDefaultScale, setHasSetDefaultScale] = useState(false);
  const [defaultScale, setDefaultScale] = useState(1.0);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setContainerWidth(entry.contentRect.width);
      }
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  const getDefaultScale = (page) => {
    const viewport = page.getViewport({ scale: 1 }); // scale=1 → intrinsic size
    const pdfWidth = viewport.width;

    const screenWidth = containerRef.current.offsetWidth;
    let scale;

    if (pdfWidth >= screenWidth) {
      scale = (screenWidth * 0.98) / pdfWidth;
    } else if (screenWidth < 800) {
      const new_pdfwidth = screenWidth * 0.9;
      scale = new_pdfwidth / pdfWidth;
    } else {
      const new_pdfwidth = screenWidth * 0.4;
      scale = new_pdfwidth / pdfWidth;
    }

    setPdfScale(scale);
    setDefaultScale(scale);
    setHasSetDefaultScale(true);
  };

  // Called when a page is loaded
  function onPageLoadSuccess(page) {
    if (!hasSetDefaultScale && containerRef.current) {
      getDefaultScale(page);
    }
  }

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

  // Zoom functions
  const zoomIn = () => {
    setPdfScale((prev) => Math.min(prev + 0.2, 3.0));
  };

  const zoomOut = () => {
    setPdfScale((prev) => Math.max(prev - 0.2, 0.5));
  };

  const resetZoom = () => {
    setPdfScale(defaultScale);
    // setPdfScale(1.0);
  };

  // Generate shareable link for attachment
  const generateShareLink = async () => {
    if (!documentPreview) return;

    setIsSharing(true);
    const result = await ShareLinkServices.get_share_link(documentPreview.id);

    if (result.success) {
      setShareUrl(result.data?.share_url);
      setShareStatus("Temporary link generated! Expires in 30 minutes.");

      // Auto-clear status after 5 seconds
      setTimeout(() => setShareStatus(""), 5000);
    } else {
      if (result.status === 400 || result.status === 409) {
        setError(result.message || "Error getting share link.");
        setShareStatus("Error generating shareable link");
        setTimeout(() => setShareStatus(""), 3000);
      } else {
        setError(
          "Error getting share link. Please ensure attachment saved first and try again.",
        );
        setShareStatus("Error generating shareable link");
        setTimeout(() => setShareStatus(""), 3000);
      }
    }
    setIsSharing(false);
  };

  // Copy share link to clipboard or trigger native sharing
  const copyShareLink = async () => {
    if (!shareUrl) {
      await generateShareLink();
      return;
    }

    // Try native sharing first (like Emergent platform)
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Shared Document: ${documentPreview?.filename || "Document"}`,
          text: "View this document (expires in 30 minutes)",
          url: shareUrl,
        });
        setShareStatus("Shared successfully!");
        setTimeout(() => setShareStatus(""), 3000);
        return;
      } catch (error) {
        if (error.name === "AbortError") {
          return; // User cancelled, don't show error
        }
        console.log("Native sharing failed, falling back to clipboard");
      }
    }

    // Fallback to clipboard
    try {
      await navigator.clipboard.writeText(shareUrl);
      setShareStatus("Link copied to clipboard!");
      setTimeout(() => setShareStatus(""), 3000);
    } catch (error) {
      setShareStatus("Failed to copy link");
      setTimeout(() => setShareStatus(""), 3000);
    }
  };

  // if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;
  if (!documentPreview) return <div className="p-4">Loading document...</div>;

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 bg-neutral-800 overflow-hidden"
    >
      {/* Top Control Bar */}
      <div className="fixed top-0 left-0 right-0 z-60 bg-[#3C3C3C] bg-opacity-70 p-4">
        <div className="flex justify-between items-center max-w-full">
          {/* Document Info */}
          <div className="bg-white px-3 py-2 rounded-md shadow-lg flex-shrink mr-3">
            <div className="flex items-center text-black">
              {documentPreview?.type === "application/pdf" ? (
                <svg
                  className="h-4 w-4 mr-2 text-red-600 flex-shrink"
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
                  className="h-4 w-4 mr-2 text-green-600 flex-shrink"
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
              <span className="text-xs font-medium truncate">
                {documentPreview.filename}
              </span>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex space-x-2 flex-shrink">
            {/* Share Button */}
            <button
              type="button"
              onClick={copyShareLink}
              disabled={isSharing}
              className="bg-black text-white px-3 py-2 rounded-md hover:bg-gray-800 disabled:bg-gray-400 transition-colors font-semibold shadow-lg flex items-center text-xs"
            >
              {isSharing ? (
                <>
                  <svg
                    className="animate-spin h-3 w-3 mr-1"
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
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  <svg
                    className="h-3 w-3 mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
                    />
                  </svg>
                  {shareUrl ? "Copy Link" : "Share"}
                </>
              )}
            </button>

            {/* Close Button */}
            <button
              type="button"
              onClick={closeFullScreenPreview}
              className="bg-white text-black px-3 py-2 rounded-md hover:bg-gray-100 transition-colors font-semibold shadow-lg text-xs"
            >
              ✕ Close
            </button>
          </div>
        </div>
      </div>

      {/* Share Status Message */}
      {shareStatus && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-60">
          <div className="bg-green-600 text-white px-4 py-2 rounded-md shadow-lg text-sm">
            {shareStatus}
          </div>
        </div>
      )}

      {/* Document Viewer */}
      <div className="absolute top-16 left-0 right-0 bottom-0 overflow-auto">
        {documentPreview.type === "application/pdf" ? (
          <div className="flex justify-center items-start min-h-full p-4">
            <div className="bg-white shadow-lg">
              {pdfError ? (
                <div className="p-8 text-center text-red-600">
                  <p className="mb-2">Error loading PDF</p>
                  <p className="text-sm">{pdfError}</p>
                </div>
              ) : (
                <Document
                  file={documentPreview.url}
                  // onLoadSuccess={onDocumentLoadSuccess}
                  // onLoadError={onDocumentLoadError}
                  loading={
                    <div className="p-8 text-center">
                      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                      <p className="mt-2 text-gray-600">Loading PDF...</p>
                    </div>
                  }
                  error={
                    <div className="p-8 text-center text-red-600">
                      <p>Failed to load PDF</p>
                    </div>
                  }
                >
                  <Page
                    pageNumber={currentPage}
                    scale={pdfScale}
                    height={undefined} // Let height auto-scale
                    width={undefined}
                    className="max-h-full max-w-full object-contain"
                    // onLoadError={onPageLoadError}
                    onLoadSuccess={onPageLoadSuccess}
                    loading={
                      <div className="p-4 text-center">
                        <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
                      </div>
                    }
                    renderTextLayer={false} // Disable text layer for better performance
                    renderAnnotationLayer={false} // Disable annotation layer for better performance
                  />
                </Document>
              )}
            </div>
          </div>
        ) : (
          <div className="w-full h-full flex items-center justify-center p-4">
            <img
              src={documentPreview.url}
              alt={documentPreview.filename}
              className="max-w-full max-h-full object-contain shadow-lg"
            />
          </div>
        )}

        {/* Bottom Control Bar */}
        <div className="fixed bottom-0 left-0 right-0 z-60 bg-[#3C3C3C] bg-opacity-70 p-4">
          <div className="flex justify-between items-center max-w-full">
            {/* PDF Controls */}
            {documentPreview.type === "application/pdf" && (
              <>
                {/* Page Navigation */}
                <div className="bg-white px-3 py-2 rounded-md shadow-lg flex-shrink mr-3">
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={prevPage}
                      disabled={currentPage <= 1}
                      className="p-1 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
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
                          strokeWidth="2"
                          d="M15 19l-7-7 7-7"
                        />
                      </svg>
                    </button>
                    <div className="flex items-center space-x-1">
                      <input
                        type="number"
                        value={currentPage}
                        onChange={(e) => goToPage(parseInt(e.target.value))}
                        min="1"
                        max={totalPages}
                        className="w-12 px-1 py-1 border border-gray-300 rounded text-center text-xs"
                      />
                      <span className="text-xs text-gray-600">
                        /{totalPages}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={nextPage}
                      disabled={currentPage >= totalPages}
                      className="p-1 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
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
                          strokeWidth="2"
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Zoom Controls */}
                <div className="bg-white px-3 py-2 rounded-md shadow-lg flex-shrink">
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={zoomOut}
                      className="p-1 bg-gray-600 text-white rounded hover:bg-gray-700"
                      title="Zoom Out"
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
                          strokeWidth="2"
                          d="M20 12H4"
                        />
                      </svg>
                    </button>
                    <span className="text-xs text-gray-600 min-w-12 text-center">
                      {Math.round(pdfScale * 100)}%
                    </span>
                    <button
                      type="button"
                      onClick={zoomIn}
                      className="p-1 bg-gray-600 text-white rounded hover:bg-gray-700"
                      title="Zoom In"
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
                          strokeWidth="2"
                          d="M12 4v16m8-8H4"
                        />
                      </svg>
                    </button>
                    <button
                      type="button"
                      onClick={resetZoom}
                      className="px-2 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700"
                      title="Reset Zoom"
                    >
                      Reset
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Share URL Display - Bottom overlay */}
        {shareUrl && shareStatus && (
          <div className="absolute bottom-4 left-4 right-4 z-60">
            <div className="bg-white px-4 py-3 rounded-md shadow-lg">
              <div className="flex items-center justify-between">
                <div className="flex-1 mr-3">
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Shareable Link:
                  </label>
                  <input
                    type="text"
                    value={shareUrl}
                    readOnly
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-xs"
                  />
                </div>
                <button
                  type="button"
                  onClick={copyShareLink}
                  className="bg-black text-white px-3 py-2 rounded-md hover:bg-gray-800 transition-colors text-xs font-medium flex-shrink"
                >
                  Copy
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
