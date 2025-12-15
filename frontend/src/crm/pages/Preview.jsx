// import "./Preview.css";
import { useState, useRef } from "react";
import ZoomVideo from "@zoom/videosdk";
import { useNavigate, useParams } from "react-router-dom";
import { useEffect } from "react";
import { Mic, MicOff, Video, VideoOff, Volume2, VolumeOff } from "lucide-react";
import { useZoom } from "../../context/ZoomContext";
import LoadingScreen from "/src/components/Loading.jsx";
import VideoPlaceHolder from "../components/VideoPlaceHolder";
import toast from "react-hot-toast";

// Request permissions first
const requestPermissions = async () => {
  try {
    await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  } catch (err) {
    console.error("Permission denied:", err);
  }
};

const mountDevices = async () => {
  await requestPermissions();
  const allDevices = await ZoomVideo.getDevices();

  const cameraDevices = allDevices.filter((device) => {
    return device.kind === "videoinput";
  });
  const micDevices = allDevices.filter((device) => {
    return device.kind === "audioinput";
  });
  const speakerDevices = allDevices.filter((device) => {
    return device.kind === "audiooutput";
  });
  return {
    mics: micDevices.map((item) => {
      return { label: item.label, deviceId: item.deviceId };
    }),
    speakers: speakerDevices.map((item) => {
      return { label: item.label, deviceId: item.deviceId };
    }),
    cameras: cameraDevices.map((item) => {
      return { label: item.label, deviceId: item.deviceId };
    }),
  };
};

const PreviewContainer = () => {
  const navigate = useNavigate();
  const { registrationId } = useParams();
  const {
    displayName,
    setDisplayName,
    setActiveMicrophone,
    setActiveSpeaker,
    setActiveCamera,
    activeCamera,
    activeMicrophone,
    activeSpeaker,
    previewVideoRef,
    previewAudioRef,
    stopPreview,
    previewMicFeedbackIntervalRef,
  } = useZoom();

  const microphoneTesterRef = useRef(null);
  const speakerTesterRef = useRef(null);

  const [isStartedVideo, setIsStartedVideo] = useState(false);
  const [isStartedAudio, setIsStartedAudio] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [isMuted, setIsMuted] = useState(true);

  const [loading, setLoading] = useState(false);
  const [micList, setMicList] = useState([]);
  const [speakerList, setSpeakerList] = useState([]);
  const [cameraList, setCameraList] = useState([]);

  const [outputLevel, setOutputLevel] = useState(0);
  const [inputLevel, setInputLevel] = useState(0);

  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  useEffect(() => {
    const getDevices = async () => {
      setLoading(true);

      const devices = await mountDevices();
      setMicList(devices.mics);
      setCameraList(devices.cameras);
      setSpeakerList(devices.speakers);

      if (devices.speakers.length > 0) {
        setActiveSpeaker(devices.speakers[0]);
      }
      if (devices.mics.length > 0) {
        setActiveMicrophone(devices.mics[0]);
        previewAudioRef.current = ZoomVideo.createLocalAudioTrack(
          devices.mics[0].deviceId,
        );
      }
      if (devices.cameras.length > 0) {
        setActiveCamera(devices.cameras[0]);
        previewVideoRef.current = ZoomVideo.createLocalVideoTrack(
          devices.cameras[0].deviceId,
        );
      }
      setLoading(false);
    };

    getDevices();
  }, []);

  const onCameraClick = async () => {
    if (isStartedVideo) {
      await previewVideoRef.current?.stop();
      setIsStartedVideo(false);
    } else {
      const videoPlayer = document.querySelector(
        `video-player[id=preview-player]`,
      );

      if (videoPlayer) {
        await previewVideoRef.current.start(videoPlayer, {
          hd: true,
          fullHd: true,
          mirrored: true,
          cropped: true,
        });
        setIsStartedVideo(true);
      }
    }
  };

  const onSwitchCamera = async (e) => {
    const deviceId = e.target.value;

    if (previewVideoRef.current) {
      if (activeCamera !== deviceId) {
        await previewVideoRef.current.switchCamera(deviceId);
        setActiveCamera(deviceId);
      }
    }
  };

  const onMicrophoneClick = async () => {
    if (isStartedAudio) {
      if (isMuted) {
        await previewAudioRef.current?.unmute();

        // Start monitoring mic level
        previewMicFeedbackIntervalRef.current = setInterval(() => {
          const level = previewAudioRef.current?.getCurrentVolume() || 0;
          setInputLevel(Math.min(100, level * 100));
        }, 100);

        setIsMuted(false);
      } else {
        if (previewMicFeedbackIntervalRef.current) {
          clearInterval(previewMicFeedbackIntervalRef.current);
        }
        await previewAudioRef.current?.mute();
        setInputLevel(0);
        setIsMuted(true);
      }
    } else {
      await previewAudioRef.current?.start();
      await previewAudioRef.current?.unmute();

      // Start monitoring mic level
      previewMicFeedbackIntervalRef.current = setInterval(() => {
        const level = previewAudioRef.current?.getCurrentVolume() || 0;
        setInputLevel(Math.min(100, level * 100));
      }, 100);

      setIsMuted(false);
      setIsStartedAudio(true);
    }
  };

  const onSwitchMicrophone = async (e) => {
    const deviceId = e.target.value;
    if (previewAudioRef.current) {
      if (activeMicrophone !== deviceId) {
        // Stop monitoring
        if (previewMicFeedbackIntervalRef.current) {
          clearInterval(previewMicFeedbackIntervalRef.current);
        }

        previewAudioRef.current.stop();
        previewAudioRef.current = ZoomVideo.createLocalAudioTrack(deviceId);
        await previewAudioRef.current?.start();

        // Restart monitoring if not muted
        if (!isMuted) {
          previewMicFeedbackIntervalRef.current = setInterval(() => {
            const level = previewAudioRef.current?.getCurrentVolume() || 0;
            setInputLevel(Math.min(100, level * 100));
          }, 100);
        }

        setActiveMicrophone(deviceId);
      }
    }
  };

  const onSpeakerClick = async () => {
    if (microphoneTesterRef.current) {
      microphoneTesterRef.current.destroy();
      microphoneTesterRef.current = null;

      setIsRecordingVoice(false);
      setIsPlayingRecording(false);
    }

    if (isPlayingAudio) {
      speakerTesterRef.current?.stop();
      speakerTesterRef.current = null;

      setIsPlayingAudio(false);
      setOutputLevel(0);
    } else {
      // Create a temporary track for testing output
      const tempTrack = ZoomVideo.createLocalAudioTrack(activeMicrophone);
      speakerTesterRef.current = tempTrack.testSpeaker({
        speakerId: activeSpeaker,
        onAnalyseFrequency: (value) => {
          setOutputLevel(Math.min(100, value));
        },
      });
      setIsPlayingAudio(true);
    }
  };

  const onSwitchSpeaker = (e) => {
    const deviceId = e.target.value;
    setActiveSpeaker(deviceId);

    if (isPlayingAudio && speakerTesterRef.current) {
      speakerTesterRef.current.stop();
      speakerTesterRef.current = ZoomVideo.createLocalAudioTrack(
        activeMicrophone,
      ).testSpeaker({
        speakerId: deviceId,
        onAnalyseFrequency: (value) => {
          setOutputLevel(Math.min(100, value));
        },
      });
    }
  };

  const handleJoin = () => {
    if (!displayName.trim().length > 0) {
      toast.error("Display name required");
      return;
    }

    if (microphoneTesterRef.current) {
      microphoneTesterRef.current.destroy();
      microphoneTesterRef.current = null;
    }

    stopPreview();
    navigate(`/video/${registrationId}`);
  };

  const handleReturn = async () => {
    try {
      stopPreview();

      if (microphoneTesterRef.current) {
        microphoneTesterRef.current.destroy();
        microphoneTesterRef.current = null;
      }
    } catch (error) {
      console.error("Error cleaning up tracks:", error);
    } finally {
      navigate(`/admin-edit/${registrationId}`);
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex-grow flex flex-col bg-gray-50">
      <div className="flex-grow flex flex-col max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 overflow-x-hidden">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Video Preview
          </h1>
          <div className="flex gap-2">
            <button
              onClick={handleReturn}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              File
            </button>
            <button
              onClick={handleJoin}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Join
            </button>
          </div>
        </div>

        <div className="flex-grow flex flex-col bg-white rounded-lg shadow-md">
          {/* Display Name */}
          <div className="flex justify-center items-center mb-4 mt-4">
            <input
              className="border-2 text-center rounded-md border-gray-300 focus:outline-none focus:ring-2  focus:ring-black"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Name"
            ></input>
          </div>

          {/* Video Preview  */}
          <VideoPlaceHolder isStartedVideo={isStartedVideo} />

          {/* Controls */}
          <div className="bg-white p-6 space-y-4">
            {/* Camera Controls */}
            <div className="flex flex-col gap-2">
              <h1 className="text-black font-semibold">Camera</h1>
              <div className="flex gap-3 items-center h-10 md:h-14">
                <button
                  onClick={onCameraClick}
                  className="px-2 py-2.5 bg-black hover:bg-gray-600 rounded-lg transition"
                >
                  {isStartedVideo ? (
                    <Video className="text-white w-5 h-5" />
                  ) : (
                    <VideoOff className="text-white w-5 h-5" />
                  )}
                </button>
                <select
                  value={activeCamera}
                  onChange={onSwitchCamera}
                  className="flex-1 min-w-0 px-3 py-3 border border-gray-600 text-white rounded-lg focus:outline-none text-sm truncate bg-black h-full"
                >
                  {cameraList.map((c) => (
                    <option key={c.deviceId} value={c.deviceId}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Microphone Controls */}
            <div className="flex flex-col gap-2">
              <h1 className="text-black font-semibold">Microphone</h1>
              <div className="flex gap-3 items-center h-10 md:h-14">
                <button
                  onClick={onMicrophoneClick}
                  className="px-2 py-2.5 bg-black hover:bg-gray-600 rounded-lg transition"
                >
                  {!isMuted ? (
                    <Mic className="text-white w-5 h-5" />
                  ) : (
                    <MicOff className="text-white w-5 h-5" />
                  )}
                </button>
                <select
                  value={activeMicrophone}
                  onChange={onSwitchMicrophone}
                  className="flex-1 items-center min-w-0 px-3 py-3 border border-gray-600 bg-black text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm truncate h-full"
                >
                  {micList.map((m) => (
                    <option key={m.deviceId} value={m.deviceId}>
                      {m.label}
                    </option>
                  ))}
                </select>
              </div>
              {!isMuted && isStartedAudio && (
                <div className="w-full h-2 bg-white border border-black rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-75"
                    style={{ width: `${inputLevel}%` }}
                  />
                </div>
              )}
            </div>

            {/* Speaker Controls */}
            <div className="flex flex-col gap-2">
              <h1 className="text-black font-semibold">Speaker</h1>
              <div className="flex gap-3 items-center h-10 md:h-14">
                <button
                  onClick={onSpeakerClick}
                  className="p-2 bg-black hover:bg-gray-600 rounded-lg transition flex-shrink-0 h-full"
                >
                  {isPlayingAudio ? (
                    <Volume2 className="text-white w-5 h-5" />
                  ) : (
                    <VolumeOff className="text-white w-5 h-5" />
                  )}
                </button>
                <select
                  value={activeSpeaker}
                  onChange={onSwitchSpeaker}
                  className="flex-1 min-w-0 px-3 py-2 border border-gray-600 bg-black text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm truncate h-full"
                >
                  {speakerList.length > 0 ? (
                    speakerList.map((m) => (
                      <option key={m.deviceId} value={m.deviceId}>
                        {m.label}
                      </option>
                    ))
                  ) : (
                    <option value="default">
                      {isMobile ? "Device Speaker" : "No speakers detected"}
                    </option>
                  )}
                </select>
              </div>

              {isPlayingAudio && (
                <div className="w-full h-2  bg-white border border-black  rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-75"
                    style={{ width: `${outputLevel}%` }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreviewContainer;
