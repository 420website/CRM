// ZoomContext.jsx
import { createContext, useContext, useRef, useState, useEffect } from "react";
import ZoomVideo from "@zoom/videosdk";
import { useNavigate } from "react-router-dom";
import { VideoServices } from "../services/videoService";

const ZoomContext = createContext(null);

export function ZoomProvider({ children }) {
  const navigate = useNavigate();
  const clientRef = useRef(null);
  const streamRef = useRef(null);
  const videoCanvasRef = useRef(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [returnUrl, setReturnUrl] = useState("admin-menu");
  const [patientSessionId, setPatientSessionId] = useState(null);

  // Local
  const [systemRequirements, setSystemRequirements] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const previewVideoRef = useRef(null);
  const previewAudioRef = useRef(null);
  const previewMicRef = useRef(null);
  const previewMicFeedbackIntervalRef = useRef(null);
  const sessionAudioRef = useRef(null);
  const sessionVideoRef = useRef(null);
  const [activeMicrophone, setActiveMicrophone] = useState("");
  const [activeSpeaker, setActiveSpeaker] = useState("");
  const [activeCamera, setActiveCamera] = useState("");
  const startLocalMediaRef = useRef();
  useEffect(() => {
    startLocalMediaRef.current = startLocalMedia;
  });
  // Session
  const [sessionConfig, setSessionConfig] = useState(null);
  const [sessionName, setSessionName] = useState(null);
  const [isInSession, setIsInSession] = useState(false);
  const [participants, setParticipants] = useState([]);
  const inSessionRef = useRef(false);
  const heartbeatTimerRef = useRef(null);

  const client = ZoomVideo.createClient();

  useEffect(() => {
    const mobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    setIsMobile(mobile);
  }, []);

  const checkSystem = () => {
    const system = ZoomVideo.checkSystemRequirements();
    const allClear = Object.keys(system).every((key) => !!system[key]);
    setSystemRequirements(allClear);
  };

  const updateParticipants = (client) => {
    const participants = client.getAllUser();
    setParticipants(participants);
  };

  // Initialize Zoom client once
  useEffect(() => {
    const initClient = async () => {
      try {
        await client.init("en-US", "Global", {
          patchJsMedia: true,
          stayAwake: true,
        });
        clientRef.current = client;
        streamRef.current = client.getMediaStream();

        // Set up event listeners
        client.on("user-added", async (payload) => {
          setParticipants(client.getAllUser());

          // Start media when YOU join
          const currentUser = client.getCurrentUserInfo();
          if (payload.some((user) => user.userId === currentUser.userId)) {
            await startLocalMediaRef.current();
          }
        });

        client.on("user-removed", (payload) => {
          // Detach video for removed users
          payload.forEach((user) => {
            try {
              stream.detachVideo(user.userId);
            } catch (err) {
              console.error(
                `Failed to detach video for user ${user.userId}:`,
                err,
              );
            }
          });

          updateParticipants(client);
        });

        client.on("user-updated", (payload) => {
          console.log("User updated:", payload);
          updateParticipants(client);
        });

        // Handle peer video state changes - following SDK docs pattern
        client.on("peer-video-state-change", async (payload) => {
          console.log("Peer video state changed:", payload);
          // const stream = client.getMediaStream();

          const stream = streamRef.current;

          if (payload.action === "Start") {
            console.log("Video started for user:", payload.userId);

            // Wait a bit for the video to be ready
            setTimeout(async () => {
              const container = document.querySelector(
                `video-player[data-user-id="${payload.userId}"]`,
              );

              if (container) {
                try {
                  await stream.attachVideo(payload.userId, 3, container);
                } catch (err) {
                  console.error(
                    `Failed to attach video for ${payload.userId}:`,
                    err,
                  );
                }
              } else {
                console.warn(`Container not found for user ${payload.userId}`);
              }

              // Update participants list
              setParticipants(client.getAllUser());
            }, 300);
          } else if (payload.action === "Stop") {
            try {
              await stream.detachVideo(payload.userId);
            } catch (err) {
              console.error(
                `Failed to detach video for ${payload.userId}:`,
                err,
              );
            }

            setParticipants(client.getAllUser());
          }
        });

        client.on("connection-change", (payload) => {
          console.log("Connection changed:", payload);
          if (payload.state === "Connected") {
            inSessionRef.current = true;
            setIsInSession(true);
          } else if (payload.state === "Closed") {
            inSessionRef.current = false;
            setIsInSession(false);
          }
        });
      } catch (err) {
        console.error("Failed to initialize Zoom client:", err);
        setError("Failed to initialize video client");
      }
    };

    initClient();

    return () => {
      if (!inSessionRef.current) return;
      if (clientRef.current) {
        leaveSession();
      }
    };
  }, []);

  // Preview
  const startPreview = async () => {
    if (!activeCamera || !activeMicrophone) return;
    console.log("hello");

    // Stop previous tracks
    if (previewVideoRef.current) await previewVideoRef.current.stop();
    if (previewAudioRef.current) await previewAudioRef.current.stop();

    // Create local tracks for preview
    previewVideoRef.current = ZoomVideo.createLocalVideoTrack(
      activeCamera.deviceId,
    );
    previewAudioRef.current = ZoomVideo.createLocalAudioTrack(
      activeMicrophone.deviceId,
    );
  };

  const stopPreview = async () => {
    if (previewVideoRef.current) {
      await previewVideoRef.current.stop();
      previewVideoRef.current = null;
    }
    if (previewAudioRef.current) {
      await previewAudioRef.current.stop();
      previewAudioRef.current = null;
    }

    if (previewMicFeedbackIntervalRef.current) {
      clearInterval(previewMicFeedbackIntervalRef.current);
      previewMicFeedbackIntervalRef.current = null;
    }
  };

  // Session
  const startHeartbeat = (patientId) => {
    sendHeartbeat(patientId);

    // then schedule periodic heartbeat
    heartbeatTimerRef.current = setInterval(() => {
      sendHeartbeat(patientId);
    }, 30000);
  };

  const stopHeartbeat = () => {
    console.log("kill heartbeat");
    console.log(heartbeatTimerRef.current);
    if (heartbeatTimerRef.current) {
      console.log("kill heartbeat2");

      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
  };

  const sendHeartbeat = async (patientId) => {
    try {
      await VideoServices.heartbeat(patientId);
    } catch (err) {
      console.error("Heartbeat failed:", err);
    }
  };

  const joinSession = async (patientId) => {
    setLoading(true);

    const client = clientRef.current;
    if (!client || !streamRef.current) {
      setError("Video client not initialized");
      setLoading(false);
      return;
    }

    try {
      // Fetch session token from backend
      const response = await VideoServices.internal_join_session(patientId);
      if (!response.success || !response.data)
        throw new Error("Failed to get session token");

      const { access_token, sessionName, sessionPasscode } = response.data;

      // console.log(activeMicrophone);
      // console.log(activeCamera);
      // console.log(activeSpeaker);
      // Join the session
      await client.join(
        sessionName,
        access_token,
        displayName,
        sessionPasscode,
      );
      // setIsInSession(true);
      setPatientSessionId(patientId);
      setSessionName(sessionName);

      // Update participants immediately
      // setParticipants(client.getAllUser());

      // Start local media
      // await startLocalMedia();

      // START HEARTBEAT
      startHeartbeat(patientId);
      // inSessionRef.current = true;
    } catch (err) {
      console.error("Failed to join session:", err);
      setError(`Failed to join session: ${err.message || err}`);
      setIsInSession(false);
    } finally {
      // Refresh participant list
      setParticipants(client.getAllUser());
      setLoading(false);
    }
  };

  const leaveSession = async () => {
    inSessionRef.current = false;
    console.log("Leaving session...");
    stopHeartbeat();

    // const stream = streamRef.current;

    try {
      await stopLocalMedia();

      const client = clientRef.current;

      if (client) {
        try {
          await client.leave();
        } catch (zoomErr) {
          // Ignore improper meeting state errors
          if (zoomErr?.errorCode === 5002) {
            console.warn("Zoom session already closed, skipping leave.");
          } else {
            console.error("Error leaving Zoom session:", zoomErr);
          }
        }
      }

      if (patientSessionId) {
        try {
          await VideoServices.leave_session(patientSessionId);
        } catch (apiErr) {
          console.warn("Failed to notify backend of leave:", apiErr);
        }
      }
    } finally {
      setIsInSession(false);
      setIsMuted(false);
      setIsVideoOn(false);
      setParticipants([]);
      navigate(returnUrl);
    }
  };

  // Local audio/video
  // Session audio/video refs
  // const sessionAudioRef = useRef(null);
  // const sessionVideoRef = useRef(null);
  //
  // const startLocalMedia = async () => {
  //   try {
  //     const client = clientRef.current;
  //     if (!client) return;
  //
  //     // AUDIO
  //     if (activeMicrophone) {
  //       if (sessionAudioRef.current) await sessionAudioRef.current.stop();
  //       sessionAudioRef.current = ZoomVideo.createLocalAudioTrack(
  //         activeMicrophone.deviceId,
  //       );
  //       await sessionAudioRef.current.start();
  //       await sessionAudioRef.current.unmute();
  //       setIsMuted(false);
  //     }
  //
  //     // VIDEO - use dedicated local video container
  //     if (activeCamera) {
  //       if (sessionVideoRef.current) await sessionVideoRef.current.stop();
  //       sessionVideoRef.current = ZoomVideo.createLocalVideoTrack(
  //         activeCamera.deviceId,
  //         { hd: true, fullHd: true },
  //       );
  //       const container = document.querySelector(".local-video-container");
  //       if (container) {
  //         await sessionVideoRef.current.start(container, {
  //           hd: true,
  //           fullHd: true,
  //           mirrored: true,
  //         });
  //         setIsVideoOn(true);
  //       } else {
  //         console.warn("Local video container not found");
  //       }
  //     }
  //   } catch (err) {
  //     console.error("Failed to start local media:", err);
  //     setError("Failed to start video/audio");
  //   }
  // };
  //
  // const stopLocalMedia = async () => {
  //   try {
  //     if (sessionVideoRef.current) {
  //       await sessionVideoRef.current.stop();
  //       sessionVideoRef.current = null;
  //       setIsVideoOn(false);
  //     }
  //     if (sessionAudioRef.current) {
  //       await sessionAudioRef.current.stop();
  //       sessionAudioRef.current = null;
  //       setIsMuted(true);
  //     }
  //   } catch (err) {
  //     console.error("Failed to stop local media:", err);
  //   }
  // };
  //
  // const toggleMute = async () => {
  //   try {
  //     const audio = sessionAudioRef.current;
  //     if (!audio) return;
  //     if (isMuted) {
  //       await audio.unmute();
  //       setIsMuted(false);
  //     } else {
  //       await audio.mute();
  //       setIsMuted(true);
  //     }
  //   } catch (err) {
  //     if (err?.message?.includes("Already")) return;
  //     console.error("Error toggling session mute:", err);
  //   }
  // };
  //
  // const toggleVideo = async () => {
  //   try {
  //     if (!activeCamera) return;
  //     if (isVideoOn) {
  //       if (sessionVideoRef.current) {
  //         await sessionVideoRef.current.stop();
  //         sessionVideoRef.current = null;
  //       }
  //       setIsVideoOn(false);
  //       return;
  //     }
  //
  //     // START VIDEO
  //     const container = document.querySelector("video-player-container");
  //     if (!container) {
  //       console.warn("Video container not found");
  //       return;
  //     }
  //     sessionVideoRef.current = ZoomVideo.createLocalVideoTrack(
  //       activeCamera.deviceId,
  //       { hd: true, fullHd: true },
  //     );
  //     await sessionVideoRef.current.start(container, {
  //       hd: true,
  //       fullHd: true,
  //       mirrored: true,
  //     });
  //     setIsVideoOn(true);
  //   } catch (err) {
  //     console.error("Error toggling session video:", err);
  //   }
  // };

  const startLocalMedia = async () => {
    try {
      const stream = streamRef.current;
      const client = clientRef.current;
      if (!client || !stream) return;

      if (activeMicrophone) {
        await stream.startAudio({
          microphoneId: activeMicrophone.deviceId,
          speakerId: activeSpeaker.deviceId,
        });
        setIsMuted(false);
      }

      if (activeCamera) {
        await stream.startVideo({
          cameraId: activeCamera.deviceId,
          hd: true,
          fullHd: true,
          mirrored: true,
        });

        console.log("Video started");
        const currentUser = client.getCurrentUserInfo();
        console.log("Current user ID:", currentUser.userId);

        // Retry finding the video-player element
        const attachWithRetry = async (attempts = 0, maxAttempts = 10) => {
          const videoPlayer = document.querySelector(
            `video-player[data-user-id="${currentUser.userId}"]`,
          );

          if (videoPlayer) {
            try {
              console.log("Attaching self video");
              await stream.attachVideo(currentUser.userId, 3, videoPlayer);
              console.log("✅ Self video attached");
            } catch (err) {
              console.error("❌ Failed to attach video:", err);
            }
          } else if (attempts < maxAttempts) {
            const delay = Math.min(100 * Math.pow(2, attempts), 1000);
            console.log(
              `video-player not found, retrying in ${delay}ms... (attempt ${attempts + 1}/${maxAttempts})`,
            );
            setTimeout(() => attachWithRetry(attempts + 1, maxAttempts), delay);
          } else {
            console.error(
              `⚠️ video-player not found after ${maxAttempts} attempts`,
            );
          }
        };

        attachWithRetry();
        setIsVideoOn(true);
      }
    } catch (err) {
      console.error("Failed to start local media:", err);
      setError("Failed to start video/audio");
    }
  };

  const stopLocalMedia = async () => {
    try {
      const stream = streamRef.current;
      if (!stream) return;

      await stream.stopVideo();
      setIsVideoOn(false);

      await stream.stopAudio();
      setIsMuted(true);
    } catch (err) {
      console.error("Failed to stop local media:", err);
    }
  };

  const toggleMute = async () => {
    try {
      const stream = streamRef.current;
      if (!stream) return;

      if (isMuted) {
        await stream.unmuteAudio();
        setIsMuted(false);
      } else {
        await stream.muteAudio();
        setIsMuted(true);
      }
    } catch (err) {
      console.error("Error toggling mute:", err);
    }
  };

  const toggleVideo = async () => {
    try {
      const stream = streamRef.current;
      const client = clientRef.current;

      if (!stream || !client) return;

      if (isVideoOn) {
        await stream.stopVideo();
        setIsVideoOn(false);
      } else {
        await stream.startVideo();
        setIsVideoOn(true);
      }
    } catch (err) {
      console.error("Error toggling video:", err);
    }
  };

  return (
    <ZoomContext.Provider
      value={{
        joinSession,
        leaveSession,
        toggleMute,
        toggleVideo,
        videoCanvasRef,
        isInSession,
        isMuted,
        isVideoOn,
        participants,
        error,
        setSessionConfig,
        sessionConfig,
        client: clientRef.current,
        stream: streamRef.current,
        zmClient: client,
        loading,
        displayName,
        setDisplayName,
        setReturnUrl,
        setPatientSessionId,
        isMobile,
        previewVideoRef,
        previewAudioRef,
        previewMicRef,
        setActiveCamera,
        activeCamera,
        setActiveSpeaker,
        activeSpeaker,
        setActiveMicrophone,
        activeMicrophone,
        startPreview,
        stopPreview,
        previewMicFeedbackIntervalRef,
        sessionVideoRef,
        sessionVideoRef,
        isInSession,
        sessionName,
        patientSessionId,
      }}
    >
      {children}
    </ZoomContext.Provider>
  );
}

export const useZoom = () => useContext(ZoomContext);
