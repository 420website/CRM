import { useState, useEffect } from "react";
import { useVoiceInput } from "../hooks/useVoiceInput";

export default function VoiceFillModal({
  setShowVoiceFillModal,
  voiceInputText,
  setVoiceInputText,
  handleVoiceFillSubmit,
}) {
  const [voiceInputStatus, setVoiceInputStatus] = useState("");
  const { transcript, isListening, speechSupported, toggleListening } =
    useVoiceInput();

  useEffect(() => {
    setVoiceInputText(transcript);
  }, [transcript]);

  if (!speechSupported) {
    return <span>Your browser does not support speech recognition.</span>;
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 shadow-lg">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            🎤 Verbal Registration
          </h3>
          <button
            type="button"
            onClick={() => setShowVoiceFillModal(false)}
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

        {/* Microphone Button */}
        <div className="mb-4 text-center">
          <button
            type="button"
            onClick={toggleListening}
            disabled={!speechSupported}
            className={`px-6 py-3 rounded-full font-medium transition-all ${
              isListening
                ? "bg-red-500 text-white hover:bg-red-600 animate-pulse"
                : "bg-blue-500 text-white hover:bg-blue-600"
            } disabled:bg-gray-400 disabled:cursor-not-allowed`}
          >
            {isListening ? "⏹️ Stop Recording" : "🎤 Start Recording"}
          </button>
        </div>

        {/* Instructions */}
        <div className="mb-4 text-sm text-gray-600 bg-gray-100 p-3 rounded-md border border-gray-200">
          <p>
            📋 Please speak your details in this order, separating each field
            naturally:
          </p>
          <ol className="list-decimal list-inside space-y-1 mt-2">
            <li>
              <strong>Name:</strong> First Last
            </li>
            <li>
              <strong>Date of Birth:</strong> "born Month Day Year"
            </li>
            <li>
              <strong>Gender:</strong> "gender Male" or "gender Female"
            </li>
            <li>
              <strong>Health Card Number:</strong> "health card 1234567890 AY"
            </li>
            <li>
              <strong>Disposition:</strong> "disposition Active"
            </li>
          </ol>
          <p className="mt-2 text-xs text-gray-500">
            You can edit the text below after speaking if anything is incorrect.
          </p>
        </div>

        {/* Voice Textarea */}
        <div className="mb-4">
          <textarea
            value={voiceInputText}
            onChange={(e) => setVoiceInputText(e.target.value)}
            rows={6}
            placeholder={`Example: 
Thomas Jefferson born August 3 1990 gender Male health card 1234567890 version A disposition Active age 35`}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
            style={{ whiteSpace: "pre-wrap" }}
          />
        </div>

        {/* Voice Status */}
        {voiceInputStatus && !voiceInputStatus.includes("Detected:") && (
          <div
            className={`text-sm mt-2 p-2 rounded-md ${
              voiceInputStatus.includes("❌")
                ? "bg-red-50 text-red-700 border border-red-200"
                : voiceInputStatus.includes("✅")
                  ? "bg-green-50 text-green-700 border border-green-200"
                  : "bg-blue-50 text-blue-700 border border-blue-200"
            }`}
          >
            {voiceInputStatus}
          </div>
        )}

        {/* Auto-Fill/Clear Button */}
        <div className="mb-3">
          <button
            type="button"
            onClick={handleVoiceFillSubmit}
            className={`w-full px-4 py-2 rounded-md font-medium transition-colors 
  bg-blue-500 text-white hover:bg-blue-600 
  disabled:bg-gray-400 disabled:text-gray-200 disabled:cursor-not-allowed`}
          >
            {"✨ Auto-Fill Fields"}
          </button>
        </div>
      </div>
    </div>
  );
}
