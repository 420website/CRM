import "./VideoGrid.css";
import { useZoom } from "../../context/ZoomContext";
import { FaCircleUser } from "react-icons/fa6";
import { Mic, MicOff } from "lucide-react";
import { useEffect, useState } from "react";

const ParticipantVideoGrid = () => {
  const { participants, clientRef, streamRef, showSelfView } = useZoom();
  const [currentPage, setCurrentPage] = useState(0);

  useEffect(() => {
    const manageVideos = async () => {
      try {
        const stream = streamRef.current;
        const client = clientRef.current;
        if (!stream || !client) return;

        await new Promise((resolve) => setTimeout(resolve, 500));

        for (const p of participants) {
          const videoPlayer = document.querySelector(
            `video-player[data-user-id="${p.userId}"]`,
          );

          if (!videoPlayer) {
            continue;
          }

          if (p.bVideoOn) {
            try {
              const container = videoPlayer.closest(".relative");
              const width = container?.clientWidth || 640;
              const height = container?.clientHeight || 360;
              await stream.attachVideo(
                p.userId,
                3, // quality (0-4, where 4 is highest)
                videoPlayer,
                width,
                height,
                0,
                0,
              );
            } catch (err) {
              console.error("Failed to attach video:", err);
            }
          } else {
            try {
              await stream.detachVideo(p.userId);
            } catch (err) {
              console.error("Video detach skipped for", p.displayName);
            }
          }
        }
      } catch (err) {
        console.error("Failed to manage videos:", err);
      }
    };

    manageVideos();
  }, [participants, clientRef, streamRef, showSelfView, currentPage]);

  let display = participants;

  // Filter out current user
  if (!showSelfView) {
    const currentUser = clientRef.current?.getCurrentUserInfo();
    display = display.filter((p) => p.userId !== currentUser?.userId);
  }

  const pages = [];
  for (let i = 0; i < display.length; i += 4) {
    pages.push(display.slice(i, i + 4));
  }
  return (
    <div className="w-full h-full flex flex-col">
      {/* Video Grid */}
      <div className="flex-1 overflow-hidden">
        {pages.length > 0 && (
          <div
            className={`h-full p-2 ${
              pages[currentPage].length === 1
                ? "grid grid-cols-1"
                : pages[currentPage].length === 2
                  ? "grid grid-rows-2 gap-2"
                  : pages[currentPage].length === 3
                    ? "grid grid-cols-2 grid-rows-2 gap-2"
                    : "grid grid-cols-2 grid-rows-2 gap-2"
            }`}
          >
            {pages[currentPage].map((participant, idx) => (
              <div
                key={participant.userId}
                className={`relative overflow-hidden rounded-lg ${
                  pages[currentPage].length === 3 && idx === 2
                    ? "col-span-2"
                    : ""
                }`}
              >
                {!participant.bVideoOn ? (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-700">
                    <FaCircleUser className="w-16 h-16 text-gray-400" />
                  </div>
                ) : (
                  <video-player-container
                    id="session-container"
                    className="w-full h-full pointer-events-none"
                    style={{ WebkitTapHighlightColor: "transparent" }}
                  >
                    <video-player
                      id="session-player"
                      data-user-id={participant.userId}
                      className="w-full h-full pointer-events-none"
                    />
                  </video-player-container>
                )}
                <div
                  className="absolute inset-0 z-10"
                  style={{
                    pointerEvents: "auto",
                    touchAction: "pan-y",
                    background: "transparent",
                  }}
                />
                <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-3 pointer-events-none z-9">
                  <div className="flex items-center gap-1">
                    <p className="text-white text-sm font-medium">
                      {participant.displayName}
                      {participant.isHost && " (Host)"}
                    </p>
                    {participant.muted === false ? (
                      <Mic size={16} className="text-white" />
                    ) : (
                      <MicOff size={16} className="text-red-600" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Page Controls */}
      {pages.length > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
            disabled={currentPage === 0}
            className="rounded text-black disabled:opacity-30"
          >
            ←
          </button>
          <span className="text-xs text-black">
            {currentPage + 1} / {pages.length}
          </span>
          <button
            onClick={() =>
              setCurrentPage((p) => Math.min(pages.length - 1, p + 1))
            }
            disabled={currentPage === pages.length - 1}
            className="rounded text-black disabled:opacity-30"
          >
            →
          </button>
        </div>
      )}
    </div>
  );
};

export default ParticipantVideoGrid;
