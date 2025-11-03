import { useMatching } from "../../hooks/useMatching";
import { useMatchTimer } from "../../hooks/useMatchTimer";
import { MatchState } from "../../types/MatchState";
import { MatchIdle } from "./MatchIdle";
import { MatchSearching } from "./MatchSearching";
import { MatchFound } from "./MatchFound";
import { MatchConfirmed } from "./MatchConfirmed";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface MatchCardProps {
  userId: string;
  category: string;
  difficulty: string;
  onMatchStateChange?: (state: MatchState) => void;
}

export function MatchCard({
  userId,
  category,
  difficulty,
  onMatchStateChange,
}: MatchCardProps) {
  const {
    matchState,
    partnerId,
    matchDetails,
    statusMessage,
    isAccepting,
    startMatching,
    cancelMatch,
    resetBackToIdle,
    acceptMatch,
  } = useMatching(userId, category, difficulty);

  const { minutes, seconds, reset, addTime } = useMatchTimer(
    matchState === MatchState.Searching || matchState === MatchState.Found,
    180,
    resetBackToIdle
  );

  const navigate = useNavigate();

  useEffect(() => {
    onMatchStateChange?.(matchState);
    // Reset timer when user cancels or returns to idle
    if (matchState === MatchState.Idle) {
      reset(180);
    }
    // Add 10 seconds when a match is found
    if (matchState === MatchState.Found) {
      addTime(10);
    }
    if (matchState === MatchState.Confirmed && matchDetails && partnerId) {
      navigate("/collabeditor", {
        state: {
          matchDetails,
          userId,
          partnerId,
        },
      });
    }
  }, [matchState]);

  const renderContent = () => {
    switch (matchState) {
      case MatchState.Idle:
        return (
          <MatchIdle
            category={category}
            difficulty={difficulty}
            statusMessage={statusMessage}
            onStart={startMatching}
          />
        );

      case MatchState.Searching:
        return (
          <MatchSearching
            minutes={minutes}
            seconds={seconds}
            statusMessage={statusMessage}
            onCancel={cancelMatch}
          />
        );

      case MatchState.Found:
        return (
          <MatchFound
            partnerName={partnerId ?? "Partner"}
            isAccepting={isAccepting}
            statusMessage={statusMessage}
            onAccept={acceptMatch}
            onForfeit={resetBackToIdle}
          />
        );

      case MatchState.Confirmed:
        return <MatchConfirmed matchDetails={matchDetails ?? 'No details'} />;

      default:
        return null;
    }
  };

  return (
    <div className="card shadow-sm border-1 border-base-200 p-10">
      {renderContent()}
    </div>
  );
}
