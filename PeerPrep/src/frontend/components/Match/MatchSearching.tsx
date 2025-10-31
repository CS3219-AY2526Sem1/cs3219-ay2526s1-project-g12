import { TimerDisplay } from './TimerDisplay';

interface MatchSearchingProps {
  minutes: string;
  seconds: string;
  statusMessage: string | null;
  onCancel: () => void;
}

export function MatchSearching({
  minutes,
  seconds,
  statusMessage,
  onCancel,
}: MatchSearchingProps) {
  return (
    <>
      <p className="text-lg font-normal mb-4">Matching in progress...</p>
      <button onClick={onCancel} className="btn btn-error mb-6">
        ❌ Cancel
      </button>
      <div className="flex justify-center gap-2">
        <TimerDisplay minutes={minutes} seconds={seconds} />
      </div>
      {statusMessage && (
        <p className="mt-4 text-sm italic text-gray-600">{statusMessage}</p>
      )}
    </>
  );
}
