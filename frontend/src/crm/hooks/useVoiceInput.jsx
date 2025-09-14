import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

export function useVoiceInput() {
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();

  if (!browserSupportsSpeechRecognition) {
    alert("Your browser does not support speech recognition.");
  }

  if (!isMicrophoneAvailable) {
    alert("Microphone not available please update permissions.");
  }

  const toggleListening = async () => {
    if (listening) {
      await SpeechRecognition.stopListening();
    } else {
      await SpeechRecognition.startListening({
        continuous: true,
        language: "en-US",
      });
      resetTranscript();
    }
  };

  return {
    transcript,
    isListening: listening,
    speechSupported: browserSupportsSpeechRecognition,
    resetTranscript,
    toggleListening,
  };
}
