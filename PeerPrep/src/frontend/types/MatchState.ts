export const MatchState = {
  Idle: 'idle',
  Searching: 'searching',
  Found: 'found',
  Confirmed: 'confirmed',
};
export type MatchState = (typeof MatchState)[keyof typeof MatchState];
