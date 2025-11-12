import { useState } from 'react';
import { matchingApi } from '../api/MatchingApi';
import { MatchState } from '../types/MatchState';

export function useMatching(
  userId: string,
  category: string,
  difficulty: string
) {
  const [matchState, setMatchState] = useState<MatchState>(MatchState.Idle);
  const [matchId, setMatchId] = useState<string | null>(null);
  const [partnerName, setPartnerName] = useState<string | null>(null);
  const [matchDetails, setMatchDetails] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isAccepting, setIsAccepting] = useState(false);

  /** Start searching for a match */
  const startMatching = async () => {
    setMatchState(MatchState.Searching);
    setStatusMessage(null);

    try {
      const res = await matchingApi.findMatch({
        user_id: userId,
        category,
        difficulty,
      });

      if (res.error) {
        console.error('Find match error:', res.error);
        setStatusMessage(res.error);
        setMatchState(MatchState.Idle);
        return;
      }

      if (res.data?.message === 'match has been found') {
        setMatchState(MatchState.Found);
        setMatchId(res.data.match_id);
        setPartnerName(res.data.partner_name || 'Your Partner');
      }
    } catch (err) {
      console.error('Find match exception:', err);
      setStatusMessage('Failed to start matching.');
      setMatchState(MatchState.Idle);
    }
  };

  /** Cancel current matching session */
  const cancelMatch = async () => {
    try {
      const res = await matchingApi.terminateMatch({
        user_id: userId,
        category,
        difficulty,
      });
      if (res.error) {
        console.error('Terminate error:', res.error);
        setStatusMessage(res.error);
      }
      console.log('Matchmaking cancelled:', res);
    } finally {
      setMatchState(MatchState.Idle);
      setMatchId(null);
      setPartnerName(null);
    }
  };

  /** Accept found match */
  const acceptMatch = async () => {
    if (!matchId) return;
    setIsAccepting(true);

    try {
      const res = await matchingApi.confirmMatch(matchId, { user_id: userId });

      if (res.error) {
        console.error('Accept match error:', res.error);
        setStatusMessage(res.error);
        return;
      }

      if (res.data?.message === 'partner failed to accept the match') {
        console.log('Partner failed to accept.');
        setStatusMessage('Partner failed to accept.');
        setMatchState(MatchState.Idle);
      } else if (res.data?.match_details) {
        setMatchDetails(res.data.match_details);
        setMatchState(MatchState.Confirmed);
      } else {
        setStatusMessage('Unexpected response during match acceptance.');
      }
    } catch (err) {
      console.error(err);
      setStatusMessage('Error accepting match.');
    } finally {
      setIsAccepting(false);
    }
  };

  /** Used in forfeit matching, and timer ends */
  const resetBackToIdle = async () => {
    setMatchState(MatchState.Idle);
  };

  return {
    matchState,
    matchId,
    partnerName,
    matchDetails,
    statusMessage,
    isAccepting,
    startMatching,
    cancelMatch,
    resetBackToIdle,
    acceptMatch,
    setMatchState,
  };
}
