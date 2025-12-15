import { useEffect } from "react";
import "./VideoGrid.css";
import { useZoom } from "../../context/ZoomContext";
import { FaCircleUser } from "react-icons/fa6";
import { Mic, MicOff } from "lucide-react";

const ParticipantVideoGrid = ({ registrationId }) => {
  const { participants, joinSession, isInSession } = useZoom();

  useEffect(() => {
    if (isInSession) return;
    joinSession(registrationId);
  }, []);

  return (
    <div className="w-full h-full">
      <div className="flex flex-col gap-2 h-full overflow-y-auto p-2">
        {participants.map((participant) => (
          <div
            key={participant.userId}
            className="relative overflow-hidden aspect-square w-full rounded-lg"
          >
            {/* Zoom SDK container */}
            <video-player-container
              id="session-container"
              className="w-full h-full pointer-events-none"
              style={{ WebkitTapHighlightColor: "transparent" }}
            >
              <video-player
                id="session-player"
                data-user-id={participant.userId}
                className="w-full h-full pointer-events-none"
                style={{ WebkitTapHighlightColor: "transparent" }}
              />
            </video-player-container>
            {/* Transparent overlay to allow scrolling */}
            <div
              className="absolute inset-0 z-10"
              style={{
                pointerEvents: "auto",
                touchAction: "pan-y",
                background: "transparent",
              }}
            />

            <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-3 pointer-events-none">
              <div className="flex items-center gap-1">
                <p className="text-white text-sm">
                  {participant.isHost ? " (Host)" : ""}
                </p>
                <p className="text-white text-sm font-medium">
                  {participant.displayName}
                </p>
                {participant.muted ? (
                  <MicOff size={16} className="text-red-700" />
                ) : (
                  <Mic size={16} className="text-white" />
                )}
              </div>
            </div>

            {!participant.bVideoOn && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
                <FaCircleUser className="w-16 h-16 text-gray-400" />
                <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-3 pointer-events-none">
                  <div className="flex items-center gap-1">
                    <p className="text-white text-sm">
                      {participant.isHost ? " (Host)" : ""}
                    </p>
                    <p className="text-white text-sm font-medium">
                      {participant.displayName}
                    </p>
                    {participant.muted ? (
                      <MicOff size={16} className="text-red-700" />
                    ) : (
                      <Mic size={16} className="text-white" />
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ParticipantVideoGrid;

// -- old --

// // ParticipantVideoGrid.jsx
// import { useEffect } from "react";
// import { useZoom } from "../../context/ZoomContext";
// import { MicOff, Mic } from "lucide-react";
// import { FaCircleUser } from "react-icons/fa6";
//
// const ParticipantVideoGrid = () => {
//   const { participants, client, stream } = useZoom();
//
//   useEffect(() => {
//     if (!client || !stream) return;
//
//     participants.forEach(async (participant) => {
//       if (!participant.bVideoOn) return;
//
//       const container = document.querySelector(
//         `[data-user-id="${participant.userId}"]`,
//       );
//       if (!container) return;
//
//       const hasVideo = container.querySelector("video-player-container");
//       if (hasVideo) return;
//
//       try {
//         const videoEl = await stream.attachVideo(participant.userId, 3);
//         container.appendChild(videoEl);
//       } catch (err) {
//         console.error(
//           `Failed to attach video for ${participant.displayName}`,
//           err,
//         );
//       }
//     });
//   }, [participants, client, stream]);
//
//   // Filter out local user from participants list
//   const remoteParticipants = participants.filter((p) => !p.isMyself);
//
//   return (
//     <div className="w-full h-full">
//       <div className="flex flex-col h-full max-h-[calc(3*200px)] overflow-y-auto">
//         {/* Local video */}
//         <div className="relative overflow-hidden bg-black mb-2">
//           <video-player-container></video-player-container>
//           <div className="local-video-container w-full h-[200px]">
//             {/* Zoom SDK injects local video here */}
//           </div>
//           <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-3 pointer-events-none">
//             <div className="flex items-center gap-1">
//               <p className="text-white text-sm font-medium">You</p>
//             </div>
//           </div>
//           <div className="absolute inset-0 flex items-center justify-center bg-gray-800 local-video-placeholder">
//             <FaCircleUser className="w-16 h-16 text-gray-400" />
//           </div>
//         </div>
//
//         {/* Remote participants */}
//         {remoteParticipants.map((participant) => (
//           <div
//             key={participant.userId}
//             className="relative overflow-hidden bg-black mb-2"
//           >
//             {/* Zoom SDK container */}
//             <div className="video-player-container w-full h-[200px]">
//               <div
//                 data-user-id={participant.userId}
//                 className="w-full h-full"
//               />
//             </div>
//             {/* Name overlay */}
//             <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-3 pointer-events-none">
//               <div className="flex items-center gap-1">
//                 <p className="text-white text-sm">
//                   {participant.isHost ? " (Host)" : ""}
//                 </p>
//                 <p className="text-white text-sm font-medium">
//                   {participant.displayName}
//                 </p>
//                 {participant.muted ? (
//                   <MicOff size={16} className="text-red-700" />
//                 ) : (
//                   <Mic size={16} className="text-white" />
//                 )}
//               </div>
//             </div>
//             {!participant.bVideoOn && (
//               <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
//                 <FaCircleUser className="w-16 h-16 text-gray-400" />
//                 {/* Name overlay */}
//                 <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-3 pointer-events-none">
//                   <div className="flex items-center gap-1">
//                     <p className="text-white text-sm">
//                       {participant.isHost ? " (Host)" : ""}
//                     </p>
//                     <p className="text-white text-sm font-medium">
//                       {participant.displayName}
//                     </p>
//                     {participant.muted ? (
//                       <MicOff size={16} className="text-red-700" />
//                     ) : (
//                       <Mic size={16} className="text-white" />
//                     )}
//                   </div>
//                 </div>
//               </div>
//             )}
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// };
//
// export default ParticipantVideoGrid;

// import { useEffect } from "react";
// import { useZoom } from "../../context/ZoomContext";
// import { FaCircleUser } from "react-icons/fa6";
// import { Mic, MicOff } from "lucide-react";
//
// const ParticipantVideoGrid = () => {
//   const { participants, client, stream } = useZoom();
//
//   useEffect(() => {
//     if (!client || !stream) return;
//
//     participants.forEach(async (participant) => {
//       if (!participant.bVideoOn) return;
//
//       const container = document.querySelector(
//         `[data-user-id="${participant.userId}"]`,
//       );
//       if (!container) return;
//
//       const hasVideo = container.querySelector("video");
//       if (hasVideo) return;
//
//       try {
//         const videoEl = await stream.attachVideo(participant.userId, 3);
//         container.appendChild(videoEl);
//       } catch (err) {
//         console.error(
//           `Failed to attach video for ${participant.displayName}`,
//           err,
//         );
//       }
//     });
//   }, [participants, client, stream]);
//
//   return (
//     <div className="w-full h-full">
//       <div className="flex flex-col h-full max-h-[calc(3*200px)] overflow-y-auto">
//         {participants.map((participant) => (
//           <div
//             key={participant.userId}
//             className="relative overflow-hidden bg-black"
//           >
//             {/* Zoom SDK container */}
//             <video-player-container
//               className="w-full h-[200px]"
//               style={{ backgroundColor: "black" }}
//             >
//               <video-player
//                 data-user-id={participant.userId}
//                 className="w-full h-full"
//               />
//             </video-player-container>
//
//             {/* Name overlay */}
//             <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-3 pointer-events-none">
//               <div className="flex items-center gap-1">
//                 <p className="text-white text-sm">
//                   {participant.isHost ? " (Host)" : ""}
//                 </p>
//                 <p className="text-white text-sm font-medium">
//                   {participant.displayName}
//                 </p>
//                 {participant.muted ? (
//                   <MicOff size={16} className="text-red-700" />
//                 ) : (
//                   <Mic size={16} className="text-white" />
//                 )}
//               </div>
//             </div>
//
//             {!participant.bVideoOn && (
//               <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
//                 <FaCircleUser className="w-16 h-16 text-gray-400" />
//               </div>
//             )}
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// };
//
// export default ParticipantVideoGrid;
