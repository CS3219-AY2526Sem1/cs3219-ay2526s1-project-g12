import { useEffect, useState, useRef } from "react";
import { matchingApi } from "../api/MatchingApi";

interface MatchCardProps {
  userId: string;
  category: string;
  difficulty: string;
}

const MatchCard = ({ userId, category, difficulty }: MatchCardProps) => {
  const [isMatching, setIsMatching] = useState(false);
  const [matchFound, setMatchFound] = useState(false);
  const [matchId, setMatchId] = useState<string | null>(null);
  const [partnerName, setPartnerName] = useState<string | null>(null);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes = 600 seconds
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [isAccepting, setIsAccepting] = useState(false);

  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [matchDetails, setMatchDetails] = useState<string | null>(null);

  // Format time mm:ss
  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return {
      minutes: m.toString().padStart(2, "0"),
      seconds: s.toString().padStart(2, "0"),
    };
  };

  // Timer countdown logic
  useEffect(() => {
    if (isMatching && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isMatching]);

  // Auto terminate when timer reaches 0
  useEffect(() => {
    if (isMatching && timeLeft === 0) {
      handleCancelMatch();
    }
  }, [timeLeft]);

  const handleStartMatch = async () => {
    setIsMatching(true);
    setMatchFound(false);
    setTimeLeft(600);
    setPartnerName(null);
    setMatchId(null);

    try {
      const res = await matchingApi.findMatch({
        user_id: userId,
        category,
        difficulty,
      });

      if (res.data && res.data.match_id) {
        // Match found
        setMatchFound(true);
        setMatchId(res.data.match_id);
        setPartnerName(res.data.partner_id || "Your partner");
        setTimeLeft((prev) => prev + 10); // +10 seconds bonus time
      } else {
        console.error("Unexpected response:", res);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCancelMatch = async () => {
    try {
      await matchingApi.terminateMatch({
        user_id: userId,
        category,
        difficulty,
      });
    } catch (err) {
      console.error(err);
    } finally {
      setIsMatching(false);
      setMatchFound(false);
      setTimeLeft(600);
      setMatchId(null);
      setPartnerName(null);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const handleAcceptMatch = async () => {
    if (!matchId) return;
    setIsAccepting(true);

    try {
      const res = await matchingApi.confirmMatch(matchId, { user_id: userId });
      if (res.error) {
        setStatusMessage(res.error);
        return;
      }
      // Case 1: partner failed to accept
      if (
        res.data &&
        res.data.message === "partner failed to accept the match"
      ) {
        setStatusMessage(
          "Partner failed to accept. Searching for another match...",
        );
        setMatchFound(false);
        setMatchDetails(null);
        setIsAccepting(false);

        // continue searching again automatically
        const retryRes = await matchingApi.findMatch({
          user_id: userId,
          category,
          difficulty,
        });

        if (retryRes.data && retryRes.data.match_id) {
          setMatchFound(true);
          setMatchId(retryRes.data.match_id);
          setPartnerName(retryRes.data.partner_id || "New partner");
          setTimeLeft((prev) => prev + 10); // +10 seconds
          setStatusMessage(null);
        }
      }
      // Case 2: success match confirmed
      else if (res.data?.match_details) {
        setStatusMessage("Match confirmed! Starting collaboration...");
        setMatchDetails(res.data.match_details);
        setIsAccepting(false);

        // Optional: stop the timer and lock UI for match start
        if (timerRef.current) clearInterval(timerRef.current);
        setIsMatching(false);

        // You can navigate or show new UI here
        // e.g., navigate("/collaboration", { state: { matchDetails: res.data.match_details } })
        console.log("Match confirmed!");
      }
    } catch (err) {
      console.error(err);
      setStatusMessage("An error occurred while confirming match.");
    } finally {
      setIsAccepting(false);
    }
  };

  const handleForfeitMatch = async () => {
    if (!matchId) return;
    try {
      setMatchFound(false);
      setMatchId(null);
      setPartnerName(null);
      await matchingApi.terminateMatch({
        user_id: userId,
        category,
        difficulty,
      });
      // Immediately find a new match — continue searching
      const res = await matchingApi.findMatch({
        user_id: userId,
        category,
        difficulty,
      });
      if (res.data && res.data.match_id) {
        setMatchFound(true);
        setMatchId(res.data.match_id);
        setPartnerName(res.data.partner_id || "New partner");
        setTimeLeft((prev) => prev + 10); // +10 seconds
      }
    } catch (err) {
      console.error(err);
    }
  };

  const { minutes, seconds } = formatTime(timeLeft);

  return (
    <div className="card shadow-sm border-1 border-base-200 p-10">
      {!isMatching && (
        <>
          {/* If match confirmed and details available */}
          {matchDetails ? (
            <>
              <p className="text-lg font-normal text-left mb-6">
                Match Confirmed!
              </p>
              <p className="text-success text-sm">
                {typeof matchDetails === "string"
                  ? matchDetails
                  : JSON.stringify(matchDetails, null, 2)}
              </p>
            </>
          ) : (
            <>
              <p className="text-lg font-normal text-left mb-6">
                Let's begin matching!
              </p>
              <button
                onClick={handleStartMatch}
                disabled={!category || !difficulty}
                className={`btn font-normal ${
                  category && difficulty
                    ? "btn-primary"
                    : "btn-disabled btn-outline"
                }`}
              >
                🔍 Match
              </button>
            </>
          )}
        </>
      )}

      {isMatching && !matchFound && (
        <>
          <p className="text-lg font-normal mb-4">Matching in progress...</p>
          <button onClick={handleCancelMatch} className="btn btn-error mb-6">
            ❌ Cancel
          </button>
          <div className="flex justify-center gap-2">
            <div className="bg-success px-6 py-3 rounded">
              <div className="text-2xl font-semibold">{minutes}</div>
              <div className="text-sm">minutes</div>
            </div>
            <div className="bg-success px-6 py-3 rounded">
              <div className="text-2xl font-semibold">{seconds}</div>
              <div className="text-sm">sec</div>
            </div>
          </div>
        </>
      )}

      {isMatching && matchFound && (
        <>
          <p className="text-lg font-normal mb-4">
            Matching found! <br /> Your partner is:{" "}
            <span className="font-semibold">{partnerName}</span>
          </p>
          <div className="flex flex-col gap-3">
            <button
              onClick={handleAcceptMatch}
              className={`btn font-normal ${
                isAccepting
                  ? "bg-gray-400 text-white cursor-not-allowed"
                  : "btn-primary"
              }`}
            >
              {isAccepting ? (
                <>
                  <span className="loading loading-spinner loading-sm mr-2"></span>
                  Accepting...
                </>
              ) : (
                "✅ Accept"
              )}
            </button>
            <button
              onClick={handleForfeitMatch}
              disabled={isAccepting}
              className="btn btn-primary font-normal"
            >
              ↩ Forfeit
            </button>
          </div>
          {statusMessage && (
            <p className="mt-4 text-sm italic">{statusMessage}</p>
          )}
        </>
      )}
    </div>
  );
};

export default MatchCard;
