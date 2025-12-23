// ZoomContext.jsx
import { createContext, useContext, useRef, useState, useEffect } from "react";
import ZoomVideo from "@zoom/videosdk";
import { useNavigate } from "react-router-dom";
import { VideoServices } from "../services/videoService";
import toast from "react-hot-toast";
import { useGuestAuth } from "./GuestAuthContext";

const ZoomContext = createContext(null);

export function ZoomProvider({ children }) {
  const navigate = useNavigate();
  const guestAuth = useGuestAuth();

  //Refs
  const clientRef = useRef(null);
  const streamRef = useRef(null);
  const isJoiningRef = useRef(false);
  const sessionAudioStartedRef = useRef(false);

  // UI States
  const [loading, setLoading] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [returnUrl, setReturnUrl] = useState("admin-menu");
  const [isMobile, setIsMobile] = useState(false);
  const [showSelfView, setShowSelfView] = useState(true);

  // Media
  const [systemRequirements, setSystemRequirements] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [isVideoOn, setIsVideoOn] = useState(false);
  const [activeMicrophone, setActiveMicrophone] = useState("");
  const [activeSpeaker, setActiveSpeaker] = useState("");
  const [activeCamera, setActiveCamera] = useState("");

  // Session
  const [isInSession, setIsInSession] = useState(false);
  const [sessionName, setSessionName] = useState(null);
  const [sessionKey, setSessionKey] = useState(null);
  const [currentUser, setCurrentUser] = useState({});
  const [participants, setParticipants] = useState([]);
  const [isSessionLocked, setIsSessionLocked] = useState(false);
  const [sessionPatientId, setSessionPatientId] = useState(null);

  //host
  const leaseIntervalRef = useRef(null);

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

  const syncParticipants = async () => {
    const users = clientRef.current.getAllUser();
    setParticipants(users);
  };

  const startLeasePolling = async (patientId) => {
    if (leaseIntervalRef.current) clearInterval(leaseIntervalRef.current);

    leaseIntervalRef.current = setInterval(async () => {
      try {
        await VideoServices.refresh_lease(patientId);
      } catch (err) {
        console.error("Failed to refresh host lease:", err);
      }
    }, 60_000);
  };

  useEffect(() => {
    if (currentUser.isHost && sessionPatientId)
      startLeasePolling(sessionPatientId);
  }, [sessionPatientId]);

  // Initialize Zoom client once
  useEffect(() => {
    const initClient = async () => {
      try {
        await client.init("en-US", "Global", {
          patchJsMedia: true,
          stayAwake: true,
          leaveOnPageUnload: true,
        });
        clientRef.current = client;
        streamRef.current = client.getMediaStream();

        // Local audio changes
        client.on("current-audio-change", (payload) => {
          const { action } = payload;

          if (action === "muted") setIsMuted(true);
          if (action === "unmute") setIsMuted(false);
        });

        // Set up event listeners
        client.on("user-added", async (payload) => {
          const currentUser = client.getCurrentUserInfo();
          if (payload.some((user) => user.userId === currentUser.userId)) {
            setCurrentUser(payload[0]);
          }

          await syncParticipants();
        });

        client.on("user-removed", async (payload) => {
          await syncParticipants();
        });

        client.on("user-updated", async (payload) => {
          await syncParticipants();
        });

        // Handle peer video state changes - following SDK docs pattern
        client.on("peer-video-state-change", async (payload) => {
          await syncParticipants();
        });

        client.on("connection-change", (payload) => {
          if (payload.state === "Connected") {
            setIsInSession(true);
          } else if (payload.state === "Closed") {
            setIsInSession(false);
          }
        });
      } catch (err) {
        toast.error("Failed to initialize video client");
      }
    };

    initClient();

    return () => {
      if (!isInSession) return;

      if (clientRef.current) {
        leaveSession();
      }
    };
  }, []);

  // Session
  const joinSession = async (patientId) => {
    if (isJoiningRef.current) return;

    setLoading(true);
    isJoiningRef.current = true;

    const client = clientRef.current;
    const stream = streamRef.current;

    if (!client || !stream) {
      toast.error("Video client not initialized");
      setLoading(false);
      isJoiningRef.current = false;
      return;
    }

    try {
      const response = await VideoServices.internalJoinVideo(patientId);

      if (!response.success && response.status === 423)
        throw new Error(response.message);

      if (!response.success || !response.data)
        throw new Error("Failed to get session token");

      const { access_token, sessionName, sessionPasscode } = response.data;

      await client.join(
        sessionName,
        access_token,
        displayName,
        sessionPasscode,
      );

      setSessionPatientId(patientId);
      setSessionKey(sessionPasscode);
      setSessionName(sessionName);
      setIsInSession(true);

      await stream.startAudio({
        microphoneId: activeMicrophone.deviceId,
        speakerId: activeSpeaker.deviceId,
        muted: true, // Start muted
      });
      sessionAudioStartedRef.current = true;

      await stream.muteAudio();
      setIsMuted(true);
    } catch (err) {
      // Ignore duplicate operation errors
      if (err.errorCode === 5012) {
        return;
      }

      if (err.message === "Session is locked.") {
        toast.error("Session is locked. Please try again later.");
        setIsInSession(false);
        setLoading(false);
        isJoiningRef.current = false;
        navigate(returnUrl);
        return;
      }

      toast.error(`Failed to join session.`);
      setIsInSession(false);
    } finally {
      setLoading(false);
      isJoiningRef.current = false;
    }
  };

  const guestJoinSession = async (patientId) => {
    if (isJoiningRef.current) return;

    setLoading(true);
    isJoiningRef.current = true;

    const client = clientRef.current;
    const stream = streamRef.current;

    if (!client || !stream) {
      toast.error("Video client not initialized");
      setLoading(false);
      isJoiningRef.current = false;
      return;
    }

    try {
      const { sessionJWT, sessionPasscode, sessionName } = guestAuth;

      await client.join(sessionName, sessionJWT, displayName, sessionPasscode);
      setSessionPatientId(patientId);
      setSessionKey(sessionPasscode);
      setSessionName(sessionName);
      setIsInSession(true);

      await stream.startAudio({
        microphoneId: activeMicrophone.deviceId,
        speakerId: activeSpeaker.deviceId,
        muted: true,
      });
      sessionAudioStartedRef.current = true;

      await stream.muteAudio();
      setIsMuted(true);
    } catch (err) {
      // Ignore duplicate operation errors
      if (err.errorCode === 5012) {
        return;
      }
      toast.error(`Failed to join session.`);
      setIsInSession(false);
    } finally {
      setLoading(false);
      isJoiningRef.current = false;
    }
  };

  const lockSession = async () => {
    const result = await VideoServices.lockSession(sessionPatientId);

    if (result.success) {
      setIsSessionLocked(true);
    } else {
      toast.error(result.message);
    }
  };

  const unlockSession = async () => {
    const result = await VideoServices.unlockSession(sessionPatientId);

    if (result.success) {
      setIsSessionLocked(false);
    } else {
      toast.error(result.message);
    }
  };
  const clearSession = () => {
    // Clear polling
    if (leaseIntervalRef.current) {
      clearInterval(leaseIntervalRef.current);
      leaseIntervalRef.current = null;
    }

    isJoiningRef.current = false;
    sessionAudioStartedRef.current = false;

    // UI States
    setLoading(false);
    setDisplayName("");
    setReturnUrl("admin-menu");
    setShowSelfView(true);

    // Media
    setSystemRequirements(false);
    setIsMuted(true);
    setIsVideoOn(false);
    setActiveMicrophone("");
    setActiveSpeaker("");
    setActiveCamera("");

    // Session
    setIsInSession(false);
    setSessionName(null);
    setSessionKey(null);
    setCurrentUser({});
    setParticipants([]);
    setIsSessionLocked(false);
    setSessionPatientId(null);
  };

  const leaveSession = async (delete_session = false) => {
    setIsInSession(false);

    try {
      if (delete_session) await VideoServices.deleteSession(sessionPatientId);

      await stopLocalMedia();

      const client = clientRef.current;

      if (client) {
        try {
          await client.leave();
        } catch (zoomErr) {
          if (zoomErr?.errorCode !== 5002) {
            console.error("Error leaving Zoom session:", zoomErr);
          }
        }
      }
    } finally {
      clearSession();
      navigate(returnUrl);
    }
  };

  // Local controls
  const stopLocalMedia = async () => {
    const stream = streamRef.current;
    if (!stream) return;

    // Stop video
    try {
      if (isVideoOn) {
        await stream.stopVideo();
        setIsVideoOn(false);
      }
    } catch (err) {
      console.error("Failed to stop video:", err);
    }

    // Stop audio
    try {
      await stream.stopAudio();
      setIsMuted(true);
    } catch (err) {
      console.error("Failed to stop audio:", err);
    }
  };

  const toggleMute = async () => {
    try {
      const stream = streamRef.current;
      if (!stream) return;

      if (!sessionAudioStartedRef.current) {
        await stream.startAudio({
          microphoneId: activeMicrophone.deviceId,
          speakerId: activeSpeaker.deviceId,
        });
        sessionAudioStartedRef.current = true;

        await stream.muteAudio();
        setIsMuted(true);
        return;
      }

      if (isMuted) {
        await stream.unmuteAudio();
        setIsMuted(false);
      } else {
        await stream.muteAudio();
        setIsMuted(true);
      }
    } catch (err) {
      toast.error("Error toggling audio");
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
        await stream.startVideo({
          cameraId: activeCamera.deviceId,
          hd: true,
          fullHd: true,
          mirrored: true,
        });
        setIsVideoOn(true);
      }
    } catch (err) {
      if (err.errorCode === 6105) {
        return;
      }
      toast.error("Error toggling video");
    }
  };

  return (
    <ZoomContext.Provider
      value={{
        joinSession,
        leaveSession,
        unlockSession,
        lockSession,
        toggleMute,
        toggleVideo,
        guestJoinSession,
        sessionName,
        isMuted,
        isVideoOn,
        isSessionLocked,
        isMobile,
        participants,
        loading,
        displayName,
        setDisplayName,
        setReturnUrl,
        setActiveCamera,
        activeCamera,
        setActiveSpeaker,
        activeSpeaker,
        setActiveMicrophone,
        activeMicrophone,
        isInSession,
        currentUser,
        isJoiningRef,
        sessionKey,
        sessionPatientId,
        clientRef,
        streamRef,
        setShowSelfView,
        showSelfView,
      }}
    >
      {children}
    </ZoomContext.Provider>
  );
}

export const useZoom = () => useContext(ZoomContext);
