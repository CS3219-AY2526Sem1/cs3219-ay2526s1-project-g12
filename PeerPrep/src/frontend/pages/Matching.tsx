import { useEffect, useState } from "react";
import NavBar from "../components/NavBar";
import { useAuth } from "../context/AuthContext";
import { questionApi } from "../api/QuestionApi";
import { MatchCard } from "../components/Match/MatchCard";
import { formatError } from "../utils/formatError";

function Matching() {
  const [topics, setTopics] = useState<string[]>([]);
  const [topic, setTopic] = useState<string | null>(null);

  const [difficulties, setDifficulties] = useState<string[]>([]);
  const [difficulty, setDifficulty] = useState<string | null>(null);

  const [loadingTopics, setLoadingTopics] = useState(false);
  const [loadingDifficulties, setLoadingDifficulties] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isMatchingActive, setIsMatchingActive] = useState(false);
  const difficultyOrder = ["Easy", "Medium", "Hard"];

  const { user } = useAuth();

  // Fetch pool categories on mount
  useEffect(() => {
    if (!user?.id) return; // early return if not logged in

    const fetchCategories = async () => {
      setLoadingTopics(true);
      setError(null);
      const res = await questionApi.getPoolCategories(user?.id);
      if (res.error) {
        setError("Failed to load topics.");
      } else if (res.data) {
        setTopics(res.data.categories);
        // default to first topic if needed
        setTopic(res.data.categories[0]);
      }
      setLoadingTopics(false);
    };

    fetchCategories();
  }, [user?.id]);

  // Fetch difficulties when topic changes
  useEffect(() => {
    if (!topic || !user?.id) {
      setDifficulties([]);
      setDifficulty(null);
      return;
    }

    const fetchDifficulties = async () => {
      setLoadingDifficulties(true);
      setError(null);
      const res = await questionApi.getPoolDifficultiesByCategory(
        user?.id,
        topic,
      );
      if (res.error) {
        setError(res.error);
        setDifficulties([]);
      } else if (res.data) {
        setDifficulties(res.data.difficulty_levels);
      }
      setLoadingDifficulties(false);
    };

    fetchDifficulties();
  }, [topic, user?.id]);

  return (
    <div className="min-h-screen flex flex-col px-20 py-10">
      <NavBar buttons={[]} />

      {error && (
        <div className="alert alert-error mb-4">
          <span>{formatError(error)}</span>
        </div>
      )}

      <h1 className="text-6xl font-semibold p-2 mb-2">Match Selection</h1>

      {/* Selection Cards */}
      <div className="flex-grow p-2">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 justify-center text-center">
          {/* Topic Selection */}
          <div className="card shadow-sm border-1 border-base-200 p-10">
            <h3 className="text-lg font-normal text-left mb-6">
              Pick your topic of choice:
            </h3>
            {loadingTopics ? (
              <p>Loading topics...</p>
            ) : (
              <select
                className="select select-bordered w-full text-center"
                value={topic ?? ""}
                onChange={(e) => {
                  setTopic(e.target.value || null);
                  setDifficulty(null);
                }}
                disabled={isMatchingActive}
              >
                <option value="" disabled>
                  Select a topic
                </option>
                {topics.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Difficulty Selection */}
          <div className="card shadow-sm border-1 border-base-200 p-10">
            <p className="text-lg font-normal text-left mb-6">
              Pick your choice of difficulty:
            </p>
            {loadingDifficulties ? (
              <p>Loading difficulties...</p>
            ) : (
              <div className="flex flex-col gap-3">
                {difficulties
                  .slice() // copy to avoid mutating state
                  .sort((a, b) => {
                    const ai = difficultyOrder.indexOf(a);
                    const bi = difficultyOrder.indexOf(b);
                    if (ai === -1 && bi === -1) return a.localeCompare(b); // both unknown
                    if (ai === -1) return 1; // a unknown → after known
                    if (bi === -1) return -1; // b unknown → after known
                    return ai - bi; // both known → sort by order
                  })
                  .map((level) => (
                    <button
                      key={level}
                      onClick={() => setDifficulty(level)}
                      disabled={!level || isMatchingActive}
                      className={`btn ${
                        difficulty === level
                          ? "btn-primary"
                          : "btn-outline btn-primary"
                      } font-normal`}
                    >
                      {level}
                    </button>
                  ))}
              </div>
            )}
          </div>

          {/* Match Button */}
          <MatchCard
            userId={user!.id}
            category={topic!}
            difficulty={difficulty!}
            onMatchStateChange={(state) =>
              setIsMatchingActive(state !== "idle")
            }
          />
        </div>
      </div>
    </div>
  );
}

export default Matching;
