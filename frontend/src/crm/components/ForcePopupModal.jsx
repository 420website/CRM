export default function ForceRegisterModal({
  handleForceSubmit,
  cancelForceSubmit,
}) {
  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg pl-5 pr-5 pt-6 pb-6 w-full max-w-md mx-4 shadow-lg">
        <h3 className="text-center text-md font-semibold text-gray-900">
          Name and DOB Match Existing Registration
        </h3>
        <p className="text-center text-sm text-gray-600 mb-4">
          Click Save to proceed anyway
        </p>

        <div className="flex space-x-3">
          <button
            type="button"
            onClick={handleForceSubmit}
            className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-medium"
          >
            Save
          </button>
          <button
            type="button"
            onClick={cancelForceSubmit}
            className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
