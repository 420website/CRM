import { useRef, useState } from "react";
import ZoomVideo from "@zoom/videosdk";

export default function App() {
  const [name, setName] = useState("");
  const [key, setKey] = useState("");
  const [token, setToken] = useState("");
  const [client, setClient] = useState(null);
  const [initialized, setInitialized] = useState(false);
  const [error, setError] = useState(null);
  const clientRef = useRef(null);
  // const streamRef = useRef(null);

  const handleInit = async () => {
    try {
      const zoomClient = ZoomVideo.createClient();
      clientRef.current = zoomClient;
      setClient(zoomClient);

      await zoomClient.init("en-US", "Global", {
        patchJsMedia: true,
        leaveOnPageUnload: false,
      });
      window.__zoomClient = zoomClient;
      console.log("intialized");

      // Set up event listeners
      zoomClient.on("user-added", async (payload) => {
        const currentUser = clientRef.current.getCurrentUserInfo();
        window.__userAdded = currentUser;
        console.log("added user");
      });

      setInitialized(true);
    } catch (err) {
      console.error("Zoom init failed", err);
      setError(err);
    }
  };

  const handleJoin = async () => {
    try {
      await client.join(name, token, "name", key);
      console.log("joined");

      window.__zoomJoined = true;
      setInitialized(true);
    } catch (err) {
      console.error("Zoom init failed", err);
      // window.__zoomInitError = String(err);
      setError(err);
    }
  };

  const handleLeave = async () => {
    try {
      await client.leave();
      console.log("joined");

      window.__zoomJoined = true;
      setInitialized(true);
    } catch (err) {
      console.error("Zoom init failed", err);
      // window.__zoomInitError = String(err);
      setError(err);
    }
  };

  const handleDelete = async () => {
    try {
      await client.leave(true);
      console.log("joined");

      window.__zoomJoined = true;
      setInitialized(true);
    } catch (err) {
      console.error("Zoom init failed", err);
      // window.__zoomInitError = String(err);
      setError(err);
    }
  };
  //
  // useEffect(() => {
  //   const initClient = async () => {
  //     try {
  //       await client.init("en-US", "Global", {
  //         patchJsMedia: true,
  //         stayAwake: true,
  //         leaveOnPageUnload: true,
  //       });
  //       clientRef.current = client;
  //       streamRef.current = client.getMediaStream();
  //
  //       // Local audio changes
  //       client.on("current-audio-change", (payload) => {
  //         const { action } = payload;
  //
  //         if (action === "muted") setIsMuted(true);
  //         if (action === "unmute") setIsMuted(false);
  //       });
  //
  //       // Set up event listeners
  //       client.on("user-added", async (payload) => {
  //         const currentUser = client.getCurrentUserInfo();
  //         if (payload.some((user) => user.userId === currentUser.userId)) {
  //           setCurrentUser(payload[0]);
  //         }
  //
  //         await syncParticipants();
  //       });
  //
  //       client.on("user-removed", async (payload) => {
  //         await syncParticipants();
  //       });
  //
  //       client.on("user-updated", async (payload) => {
  //         await syncParticipants();
  //       });
  //
  //       // Handle peer video state changes - following SDK docs pattern
  //       client.on("peer-video-state-change", async (payload) => {
  //         await syncParticipants();
  //       });
  //
  //       client.on("connection-change", (payload) => {
  //         if (payload.state === "Connected") {
  //           setIsInSession(true);
  //         } else if (payload.state === "Closed") {
  //           setIsInSession(false);
  //         }
  //       });
  //     } catch (err) {
  //       toast.error("Failed to initialize video client");
  //     }
  //   };
  //
  //   initClient();
  //
  //   return () => {
  //     if (!isInSession) return;
  //
  //     if (clientRef.current) {
  //       leaveSession();
  //     }
  //   };
  // }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Zoom SDK Test</h1>
      <button id="initButton" onClick={handleInit} disabled={initialized}>
        {initialized ? "Initialized" : "Initialize Zoom"}
      </button>

      <div style={{ marginBottom: 10 }}>
        <label>
          Name:{" "}
          <input
            type="text"
            id="sessionName"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
      </div>
      <div style={{ marginBottom: 10 }}>
        <label>
          Key:{" "}
          <input
            type="text"
            id="sessionKey"
            value={key}
            onChange={(e) => setKey(e.target.value)}
          />
        </label>
      </div>

      <div style={{ marginBottom: 10 }}>
        <label>
          Token:{" "}
          <input
            type="text"
            id="accessToken"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
        </label>
      </div>

      <button id="joinButton" onClick={handleJoin}>
        Join
      </button>

      <button id="leaveButton" onClick={handleLeave}>
        Leave
      </button>

      <button id="deleteButton" onClick={handleDelete}>
        Delete
      </button>

      {error && (
        <div style={{ marginTop: 10, color: "red" }}>Error: {error}</div>
      )}
    </div>
  );
}
