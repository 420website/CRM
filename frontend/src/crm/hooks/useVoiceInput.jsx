import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

export function useVoiceInput() {
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  const toggleListening = () => {
    if (listening) {
      SpeechRecognition.stopListening();
    } else {
      SpeechRecognition.startListening({
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
