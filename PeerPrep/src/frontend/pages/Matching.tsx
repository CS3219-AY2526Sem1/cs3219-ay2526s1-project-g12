import { useState } from "react";
import NavBar from "../components/NavBar";

function Matching() {
  const [topic, setTopic] = useState("String");
  const [difficulty, setDifficulty] = useState<string | null>(null);

  const topics = [
    "Array",
    "String",
    "Dynamic Programming",
    "Hash Table",
    "Graph",
  ];

  const handleMatch = () => {
    if (!topic || !difficulty) {
      alert("Please select both topic and difficulty!");
      return;
    }
    console.log(`Matching with: ${topic} - ${difficulty}`);
    // Add navigation or API call to initiate match here
  };

  return (
    <div className="min-h-screen flex flex-col px-20 py-10">
      <NavBar buttons={[]} />

      <h1 className="text-6xl font-semibold p-2 mb-2">Match Selection</h1>

      {/* Selection Cards */}
      <div className="flex-grow p-2">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 justify-center text-center">
          {/* Topic Selection */}
          <div className="card shadow-sm border-1 border-base-200 p-10">
            <h3 className="text-lg font-normal text-left mb-6">
              Pick your topic of choice:
            </h3>
            <select
              className="select select-bordered w-full text-center"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            >
              {topics.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty Selection */}
          <div className="card shadow-sm border-1 border-base-200 p-10">
            <p className="text-lg font-normal text-left mb-6">
              Pick your choice of difficulty:
            </p>
            <div className="flex flex-col gap-3">
              {["Easy", "Medium", "Hard"].map((level) => (
                <button
                  key={level}
                  onClick={() => setDifficulty(level)}
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
          </div>

          {/* Match Button */}
          <div className="card shadow-sm border-1 border-base-200 p-10">
            <p className="text-lg font-normal text-left mb-6">
              Let's begin matching!
            </p>
            <button
              onClick={handleMatch}
              className="btn btn-primary font-normal"
            >
              🔍 Match
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Matching;
