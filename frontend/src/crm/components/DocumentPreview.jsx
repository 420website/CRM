export default function DocumentPreviewModal() {
  return (
    <div>
      (documentPreview.type === "pdf" || documentPreview.type === "image") && (
      <div className="fixed inset-0 z-50 bg-black overflow-hidden">
        {/* Top Control Bar - Fixed positioning with safe area */}
        <div className="absolute top-0 left-0 right-0 z-60 bg-black bg-opacity-50 p-4">
          <div className="flex justify-between items-center max-w-full">
            {/* Document Info */}
            <div className="bg-white px-3 py-2 rounded-md shadow-lg flex-shrink-0 mr-3">
              <div className="flex items-center text-black">
                {documentPreview.type === "pdf" ? (
                  <svg
                    className="h-4 w-4 mr-2 text-red-600 flex-shrink-0"
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
                    className="h-4 w-4 mr-2 text-green-600 flex-shrink-0"
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

            {/* Page Navigation for PDFs */}
            {documentPreview.type === "pdf" && (
              <div className="bg-white px-3 py-2 rounded-md shadow-lg flex-shrink-0 mr-3">
                <div className="flex items-center space-x-2">
                  <button
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
                    <span className="text-xs text-gray-600">/{totalPages}</span>
                  </div>

                  <button
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
            )}

            {/* Control Buttons */}
            <div className="flex space-x-2 flex-shrink-0">
              {/* Share Button */}
              <button
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

        {/* Document Viewer - Positioned below controls */}
        <div className="absolute top-16 left-0 right-0 bottom-0">
          {documentPreview.type === "pdf" ? (
            <iframe
              src={`${documentPreview.url}#toolbar=1&navpanes=1&scrollbar=1&view=FitV&zoom=100`}
              className="w-full h-full"
              title="Full Screen PDF Preview"
              style={{ border: "none" }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center p-4">
              <img
                src={documentPreview.url}
                alt={documentPreview.filename}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          )}
        </div>

        {/* Share URL Display - Bottom overlay */}
        {shareUrl && (
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
                  onClick={copyShareLink}
                  className="bg-black text-white px-3 py-2 rounded-md hover:bg-gray-800 transition-colors text-xs font-medium flex-shrink-0"
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
