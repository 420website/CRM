import { useState, useEffect } from "react";
import { useVoiceInput } from "../hooks/useVoiceInput";

export default function VoiceInput({ voiceInputText, setVoiceInputText }) {
  const [voiceInputStatus, setVoiceInputStatus] = useState("");
  const { transcript, isListening, speechSupported, toggleListening } =
    useVoiceInput();

  useEffect(() => {
    setVoiceInputText(transcript);
  }, [transcript]);

  return (
    <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-md">
      <h3 className="text-sm font-medium text-gray-700 mb-3">
        🎤 Verbal Registration: Record all details at once, then auto-populate
        fields
      </h3>

      {/* Microphone Control Button */}
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

      {/* Voice Text Area (Blank) */}
      <div className="mb-3">
        <textarea
          value={voiceInputText}
          onChange={(e) => setVoiceInputText(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          rows="4"
          placeholder=""
          style={{ whiteSpace: "pre-wrap" }}
        />
      </div>

      {/* Voice Status - Only show success messages, not detection messages */}
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
    </div>
  );
}
