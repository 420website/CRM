export default function PaginationControls() {
  return (
    // Pagination Component - Mobile Responsive
    <div className="flex flex-col sm:flex-row items-center justify-between mt-6 px-4 py-3 bg-gray-50 rounded-lg gap-4">
      <div className="flex items-center gap-2 text-sm text-gray-600 text-center sm:text-left">
        <span>
          Showing {(currentPage - 1) * pageSize + 1} to{" "}
          {Math.min(currentPage * pageSize, totalRecords)} of {totalRecords}{" "}
          results
        </span>
      </div>

      <div className="flex items-center gap-2 flex-wrap justify-center">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage <= 1 || loading}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
        >
          Previous
        </button>

        <div className="flex items-center gap-1 flex-wrap">
          {[...Array(Math.min(5, totalPages))].map((_, i) => {
            let pageNum;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }

            return (
              <button
                key={pageNum}
                onClick={() => handlePageChange(pageNum)}
                disabled={loading}
                className={`px-3 py-1 text-sm rounded-md ${
                  pageNum === currentPage
                    ? "bg-black text-white"
                    : "border border-gray-300 hover:bg-gray-100"
                } disabled:opacity-50`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage >= totalPages || loading}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
        >
          Next
        </button>
      </div>
    </div>
  );
}
