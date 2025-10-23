interface MatchIdleProps {
  category: string;
  difficulty: string;
  statusMessage: string | null;
  onStart: () => void;
}

export function MatchIdle({
  category,
  difficulty,
  statusMessage,
  onStart,
}: MatchIdleProps) {
  const disabled = !category || !difficulty;

  return (
    <>
      <p className="text-lg font-normal text-left mb-6">
        Let's begin matching!
      </p>
      <button
        onClick={onStart}
        disabled={disabled}
        className={`btn font-normal w-full ${
          disabled ? "btn-disabled btn-outline" : "btn-primary"
        }`}
      >
        🔍 Match
      </button>
      {disabled && (
        <p className="text-sm mt-3 italic">
          Please select both topic and difficulty before matching.
        </p>
      )}
      {statusMessage && (
        <p className="mt-4 text-sm italic text-gray-600">{statusMessage}</p>
      )}
    </>
  );
}
