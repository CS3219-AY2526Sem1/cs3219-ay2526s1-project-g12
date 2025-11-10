interface MatchConfirmedProps {
  matchDetails: string | object;
}

export function MatchConfirmed({ matchDetails }: MatchConfirmedProps) {
  return (
    <>
      <p className="text-lg font-normal text-left mb-6">
        ✅ Match Confirmed! Redirecting to collaboration room...
      </p>
      <div className="border rounded-lg p-5 text-left">
        <h3 className="font-medium mb-2">Match Details</h3>
        <pre className="text-sm text-success whitespace-pre-wrap">
          {typeof matchDetails === 'string'
            ? matchDetails
            : JSON.stringify(matchDetails, null, 2)}
        </pre>
      </div>
    </>
  );
}
