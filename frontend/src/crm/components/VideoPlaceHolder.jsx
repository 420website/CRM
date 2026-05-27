import { FaCircleUser } from "react-icons/fa6";
import "./VideoPlaceHolder.css";

export default function VideoPlaceHolder({ isStartedVideo }) {
  return (
    <div className="w-full px-6">
      <div className="bg-gray-200 relative w-full aspect-[9/16] sm:aspect-[16/9] overflow-hidden">
        <video-player-container id="preview-container">
          <video-player id="preview-player" />
        </video-player-container>

        {!isStartedVideo && (
          <div className="absolute inset-0 flex items-center justify-center">
            <FaCircleUser className="w-16 h-16 text-gray-400" />
          </div>
        )}
      </div>
    </div>
  );
}
