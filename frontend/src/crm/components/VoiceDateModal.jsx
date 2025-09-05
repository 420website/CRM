export default function VoiceDateModal({
  voiceDateInput,
  setVoiceDateInput,
  handleVoiceDateSubmit,
  setShowVoiceDateModal,
}) {
  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            🎤 Voice Date Input
          </h3>
          <button
            type="button"
            onClick={() => setShowVoiceDateModal(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">
            Tap the text field below and use your phone's microphone to speak
            the date:
          </p>
          <input
            type="text"
            value={voiceDateInput}
            onChange={(e) => setVoiceDateInput(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Say: 'August third nineteen sixty five' or 'today'"
            autoFocus
          />
        </div>

        <div className="mb-4 text-xs text-gray-500">
          <strong>Examples:</strong>
          <br />• "August third nineteen sixty five"
          <br />• "January fifteenth twenty twenty four"
          <br />• "Today" or "Yesterday"
          <br />• "Fifteenth of January twenty twenty four"
        </div>

        <div className="flex space-x-3">
          <button
            type="button"
            onClick={handleVoiceDateSubmit}
            className="flex-1 bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors font-medium"
          >
            Set Date
          </button>
          <button
            type="button"
            onClick={() => setShowVoiceDateModal(false)}
            className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
