export default function DeleteConfirmModal({
  message,
  confirmDelete,
  setShowDeleteConfirm,
}) {
  return (
    // In your JSX:
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg max-w-sm mx-4">
        <h3 className="font-bold mb-2">{message}</h3>
        <p className="mb-4">This action cannot be undone.</p>
        <div className="flex gap-2">
          <button
            onClick={() => {
              confirmDelete();
              setShowDeleteConfirm(false);
            }}
            className="bg-red-500 text-white px-4 py-2 rounded"
          >
            Delete
          </button>
          <button
            onClick={() => setShowDeleteConfirm(false)}
            className="bg-gray-300 px-4 py-2 rounded"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
