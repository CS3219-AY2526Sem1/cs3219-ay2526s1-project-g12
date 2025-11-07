interface TopBarProps {
  onExit?: () => void;
  category: string;
  difficulty: string;
  minutes: string;
  seconds: string;
  partnerName: string;
  isMuted?: boolean;
  onToggleMute?: () => void;
  isSpeaking?: boolean;
}

export function TopBar({
  onExit,
  category,
  difficulty,
  minutes,
  seconds,
  partnerName,
  isMuted = true,
  onToggleMute,
  isSpeaking = false,
}: TopBarProps) {
  return (
    <div className="navbar mb-2">
      <div className="flex">
        <span className="peerprep-logo mt-[5%]">PeerPrep</span>
      </div>

      <div className="flex-1"></div>

      <div className="flex gap-4">
        <div className="flex flex-col bg-gray-100 px-4 py-2 rounded-xl">
          <span className="font-medium text-base">Time Elapsed</span>
          <span className="font-extrabold text-4xl">
            {minutes}m {seconds}s
          </span>
          <span className="font-medium">
            Category: {category} | Difficulty: {difficulty}
          </span>
        </div>

        <div className="flex flex-col bg-gray-100 px-4 py-2 rounded-xl">
          <span className="font-medium text-base">Your matched partner</span>
          <span className="font-extrabold text-4xl">{partnerName}</span>
        </div>

        <div className="flex flex-col gap-2">
          <button onClick={onExit} className="btn btn-error font-normal">
            ➜] Exit
          </button>

          {onToggleMute && (
            <div className="relative flex items-center gap-2">
              <button
                onClick={onToggleMute}
                className={`btn font-normal ${
                  isMuted ? "btn-warning" : "btn-success text-white"
                }`}
              >
                {isMuted ? "🔇 Unmute Mic" : "🎙️ Mute Mic"}
              </button>

              {/* Glowing Dot */}
              {!isMuted && (
                <div
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    isSpeaking
                      ? "bg-green-400 shadow-[0_0_8px_3px_rgba(34,197,94,0.7)]"
                      : "bg-gray-300"
                  }`}
                ></div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
