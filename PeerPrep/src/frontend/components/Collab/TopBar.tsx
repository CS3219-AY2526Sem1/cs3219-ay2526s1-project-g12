interface TopBarProps {
  onExit?: () => void;
  category: string;
  difficulty: string;
  minutes: string;
  seconds: string;
}

export function TopBar({ onExit, category, difficulty, minutes, seconds }: TopBarProps) {
  return (
    <div className="navbar mb-2">
      <div className="flex">
        <span className="peerprep-logo mt-[5%]">PeerPrep</span>
      </div>

      <div className="flex-1"></div>

      <div className="flex gap-4">
        <div className="flex flex-col bg-gray-100 px-4 py-2 rounded-xl">
          <span className="font-medium text-base">Time Elapsed</span>
          <span className="font-extrabold text-4xl">{minutes}m {seconds}s</span>
          <span className="font-medium">
            Category: {category} | Difficulty: {difficulty}
          </span>
        </div>

        <div className="flex flex-col bg-gray-100 px-4 py-2 rounded-xl">
          <span className="font-medium text-base">Your matched partner</span>
          <span className="font-extrabold text-4xl">Gavin Sin</span>
          <span className="text-success font-medium">CONNECTED</span>
        </div>

        <div className="flex flex-col gap-2">
          <button onClick={onExit} className="btn btn-error font-normal">
            ➜] Exit
          </button>
        </div>
      </div>
    </div>
  );
}
