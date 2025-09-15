import { useEffect, useRef, useState } from "react";

import { Document, Page, pdfjs } from "react-pdf";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

export default function DocumentPreview({
  documentPreview,
  totalPages,
  openFullScreenPreview,
}) {
  const [currentPage, setCurrentPage] = useState(1);
  const [hasSetDefaultScale, setHasSetDefaultScale] = useState(false);
  const [defaultScale, setDefaultScale] = useState(1.0);
  const [pdfScale, setPdfScale] = useState(1.0);
  const containerRef = useRef(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState(null);
  const [containerWidth, setContainerWidth] = useState(0);
  const [containerHeight, setContainerHeight] = useState(0);
  const [pageAspectRatio, setPageAspectRatio] = useState(1);

  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setContainerWidth(entry.contentRect.width);
        setContainerHeight(entry.contentRect.height);
      }
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  const onPageLoadSuccess = (page) => {
    setPageAspectRatio(page.originalWidth / page.originalHeight);
  };

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

  // PDF event handlers
  const onDocumentLoadSuccess = () => {
    setPdfLoading(false);
    setPdfError(null);
  };

  const onDocumentLoadError = () => {
    setPdfError("Failed to load PDF document");
    setPdfLoading(false);
  };

  return (
    <div className="space-y-4">
      {/* PDF Preview */}
      <div
        ref={containerRef}
        className="border-2 border-gray-300 rounded-lg overflow-hidden shadow-md flex items-center justify-center"
        style={{ height: "600px" }}
      >
        <Document
          file={documentPreview.url}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
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
            width={
              containerWidth < containerHeight * pageAspectRatio
                ? containerWidth
                : undefined
            }
            height={
              containerWidth >= containerHeight * pageAspectRatio
                ? containerHeight
                : undefined
            }
            className="max-h-full max-w-full object-contain"
            loading={
              <div className="p-4 text-center">
                <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
              </div>
            }
            onLoadSuccess={onPageLoadSuccess}
            renderTextLayer={false} // Disable text layer for better performance
            renderAnnotationLayer={false} // Disable annotation layer for better performance
          />
        </Document>
      </div>

      {/* Navigation Controls - Clean Layout */}
      <div className="bg-gray-50 border rounded-lg p-4">
        <div className="flex items-center justify-between max-w-md mx-auto">
          <button
            type="button"
            onClick={prevPage}
            disabled={currentPage <= 1}
            className="px-2 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
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
            <span className="text-sm text-gray-600">of {totalPages}</span>
          </div>

          <button
            type="button"
            onClick={nextPage}
            disabled={currentPage >= totalPages}
            className="px-2 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
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
  );
}
