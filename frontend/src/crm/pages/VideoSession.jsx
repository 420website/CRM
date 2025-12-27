import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { useZoom } from "../../context/ZoomContext";
import { HiMiniUsers } from "react-icons/hi2";
import { Mic, MicOff, Video, VideoOff } from "lucide-react";
import ParticipantVideoGrid from "../components/VideoGrid";
import { FiShare2, FiCheck } from "react-icons/fi";
import ConfirmModal from "../components/ConfirmModal";
import LoadingScreen from "/src/components/Loading.jsx";
import { PictureInPicture, PictureInPicture2 } from "lucide-react";
import { Lock, Unlock, Settings } from "lucide-react";

export default function VideoSession() {
  const { patientId } = useParams();
  const [copied, setCopied] = useState(false);
  const [showConfirm, setShowConfirm] = useState("");
  const [showUsers, setShowUsers] = useState(false);

  const {
    leaveSession,
    toggleMute,
    toggleVideo,
    isMuted,
    isVideoOn,
    participants,
    sessionPatientId,
    sessionKey,
    currentUser,
    isSessionLocked,
    lockSession,
    unlockSession,
    loading,
    isJoiningRef,
    joinSession,
    setShowSelfView,
    showSelfView,
  } = useZoom();

  useEffect(() => {
    if (isJoiningRef.current) return;

    joinSession(patientId);
  }, []);

  const copyMeetingInfo = () => {
    const guestUrl = `${window.location.origin}/guest-video/${sessionPatientId}`;
    const text = `Join the video session:

URL: ${guestUrl}
Passcode: ${sessionKey}`;

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExit = () => {
    if (currentUser?.isHost) {
      const confirmed = window.confirm("End session for all participants?");
      if (!confirmed) return;
      leaveSession(true);
    } else {
      leaveSession();
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex-grow flex flex-col bg-gray-50">
      <div className="flex-grow flex flex-col bg-white rounded-lg shadow-md">
        {showConfirm === "delete" && (
          <ConfirmModal
            message={"Confirm to delete registration"}
            subMessage={"This action cannot be undone"}
            confirm={() => deleteRegistration(deleteRegistrationId)}
            setShowConfirm={setShowConfirm}
          />
        )}

        {/* Participants Sidebar */}
        <div className="bg-white flex flex-col rounded-lg shadow-md p-4 m-4">
          <div className="flex w-full mb-1">
            <div className="flex justify-between items-center w-full">
              <div className="flex gap-2 items-center">
                <h3 className="text-black font-semibold">
                  Patient: {sessionPatientId}
                </h3>
                {currentUser?.isHost &&
                  (isSessionLocked ? (
                    <button onClick={unlockSession} title="Unlock session">
                      <Lock className="w-4 h-4 text-black font-bold" />
                    </button>
                  ) : (
                    <button onClick={lockSession} title="Lock session">
                      <Unlock className="w-4 h-4" />
                    </button>
                  ))}
              </div>

              <button onClick={() => setShowUsers(!showUsers)} title="Settings">
                <Settings className="w-4 h-4" />
              </button>
            </div>
            <div className="flex gap-2 items-center">
              <div className="relative">
                {showUsers && (
                  <div className="absolute right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg min-w-[200px] z-20">
                    {/* Settings Header */}
                    <div className="border-b border-gray-200 px-3 py-2">
                      <div className="flex justify-between items-center">
                        <h3 className="font-bold text-gray-900">Settings</h3>
                        <button
                          onClick={copyMeetingInfo}
                          className="flex items-center gap-1 text-gray-600 hover:text-blue-600 hover:bg-gray-50 rounded text-xs px-2 py-1"
                        >
                          {copied ? (
                            <FiCheck className="w-3 h-3 text-green-600" />
                          ) : (
                            <FiShare2 className="w-3 h-3 " />
                          )}
                          Share
                        </button>
                      </div>
                    </div>

                    {/* Action Buttons */}

                    {/* Participants Section */}
                    <div className="px-3 py-2">
                      <div className="flex items-center gap-2 mb-0">
                        <HiMiniUsers className="w-4 h-4 text-gray-700" />
                        <h4 className="text-sm font-semibold text-gray-700">
                          ({participants.length})
                        </h4>
                      </div>

                      {/* Participants List */}
                      <div className="max-h-[180px] overflow-y-auto space-y-1">
                        {participants
                          .sort((a, b) => {
                            if (a.isHost && !b.isHost) return -1;
                            if (!a.isHost && b.isHost) return 1;
                            return a.displayName.localeCompare(b.displayName);
                          })
                          .map((user) => (
                            <div
                              key={user.userId}
                              className="flex items-center justify-between gap-3 pr-2 py-2 hover:bg-gray-50 rounded"
                            >
                              <div className="flex-1 min-w-0">
                                <span className="text-sm font-medium break-words">
                                  {user.displayName}
                                </span>
                                {user.isHost && (
                                  <span className="text-xs text-gray-500 ml-1">
                                    (Host)
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center gap-2 flex-shrink-0">
                                {user.muted === false ? (
                                  <Mic size={14} className="text-gray-500" />
                                ) : (
                                  <MicOff size={14} className="text-red-500" />
                                )}
                                {user.bVideoOn ? (
                                  <Video size={14} className="text-gray-500" />
                                ) : (
                                  <VideoOff
                                    size={14}
                                    className="text-red-500"
                                  />
                                )}
                              </div>
                            </div>
                          ))}
                      </div>
                      <div className="border-t border-gray-200 flex gap-1 p-1">
                        <button
                          onClick={() => setShowSelfView(!showSelfView)}
                          className={`flex-1 flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs ${
                            showSelfView
                              ? "text-blue-600 bg-blue-50"
                              : "text-gray-600 hover:bg-gray-50"
                          }`}
                        >
                          {showSelfView ? (
                            <>
                              <PictureInPicture className="w-3 h-3" />
                              Hide Me
                            </>
                          ) : (
                            <>
                              <PictureInPicture2 className="w-3 h-3" />
                              View Me
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="h-[80vh]">
            <ParticipantVideoGrid />
          </div>
          {/* Control Bar */}
          <div className="flex justify-center items-center gap-4 pt-4">
            {/* Mute/Unmute Button */}
            <button
              onClick={toggleMute}
              className={`p-3 rounded-full ${
                isMuted
                  ? "bg-red-500 hover:bg-red-600"
                  : "bg-gray-700 hover:bg-gray-600"
              } text-white transition-colors`}
              title={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? (
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>

            {/* Video On/Off Button */}
            <button
              onClick={toggleVideo}
              className={`p-3 rounded-full ${
                !isVideoOn
                  ? "bg-red-500 hover:bg-red-600"
                  : "bg-gray-700 hover:bg-gray-600"
              } text-white transition-colors`}
              title={isVideoOn ? "Stop Video" : "Start Video"}
            >
              {isVideoOn ? (
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z"
                    clipRule="evenodd"
                  />
                  <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                </svg>
              )}
            </button>

            {/* Leave Button */}
            <button
              onClick={handleExit}
              className="p-3 rounded-full bg-red-500 hover:bg-red-600 text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
