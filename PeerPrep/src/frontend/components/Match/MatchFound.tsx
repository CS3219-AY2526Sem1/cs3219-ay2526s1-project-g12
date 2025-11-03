interface MatchFoundProps {
  partnerName: string;
  isAccepting: boolean;
  statusMessage: string | null;
  onAccept: () => void;
  onForfeit: () => void;
}

export function MatchFound({
  partnerName,
  isAccepting,
  statusMessage,
  onAccept,
  onForfeit,
}: MatchFoundProps) {
  return (
    <>
      <p className="text-lg font-normal mb-4">
        Matching found! <br /> Your partner is:{' '}
        <span className="font-semibold">{partnerName}</span>
      </p>
      <div className="flex flex-col gap-3">
        <button
          onClick={onAccept}
          disabled={isAccepting}
          className={`btn font-normal ${
            isAccepting ? 'bg-gray-400 cursor-not-allowed' : 'btn-primary'
          }`}
        >
          {isAccepting ? (
            <>
              <span className="loading loading-spinner loading-sm mr-2"></span>
              Accepting...
            </>
          ) : (
            '✅ Accept'
          )}
        </button>
        <button
          onClick={onForfeit}
          disabled={isAccepting}
          className="btn btn-primary font-normal"
        >
          ↩ Forfeit
        </button>
      </div>

      {statusMessage && (
        <p className="mt-4 text-sm italic text-gray-600">{statusMessage}</p>
      )}
    </>
  );
}
