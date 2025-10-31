import { useEffect, useState } from 'react';
import NavBar from '../components/NavBar';
import { NAV_BUTTONS } from '../config/NavConfig';
import { useAuth } from '../context/AuthContext';
import {
  questionHistoryApi,
  type QuestionHistory,
} from '../api/QuestionHistoryApi';

function Dashboard() {
  const { user } = useAuth();
  const [userAttemptHistory, setUserAttemptHistory] = useState<
    QuestionHistory[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.id) return;

    const fetchAttempts = async () => {
      setLoading(true);
      setError(null);
      const res =
        await questionHistoryApi.get_question_history_details_by_user_id();
      if (res.error) {
        setError('Failed to load user attempts.');
      } else if (res.data) {
        setUserAttemptHistory(res.data);
      }
      setLoading(false);
    };

    fetchAttempts();
  }, []);

  const summariseTime = (uah: QuestionHistory[]) => {
    const totalTime: number = uah
      .map((attempt) => attempt.time_elapsed)
      .reduce((a, b) => a + b, 0);
    const hours = totalTime / 60 / 60;
    const minutes = (totalTime / 60) % 60;
    return `${hours.toFixed(0)}h ${minutes.toFixed(0)}m`;
  };

  return (
    <div className="min-h-screen px-20 py-10">
      <NavBar buttons={NAV_BUTTONS} />

      {/* Welcome Section */}
      <h1 className="text-6xl font-semibold p-2">
        Welcome, {user?.first_name} {user?.last_name}
      </h1>
      <p className="text-2xl p-2 font-light tracking-widest">For your review</p>

      {loading ? (
        <div className="flex p-2 gap-6">
          <div className="card w-72 card-xs shadow-sm border-1 border-base-200">
            <div className="card-body p-4 gap-0.5">
              <h2 className="font-extrabold text-4xl">Loading...</h2>
            </div>
          </div>
        </div>
      ) : error ? (
        <div className="flex p-2 gap-6">
          <div className="card w-72 card-xs shadow-sm border-1 border-base-200">
            <div className="card-body p-4 gap-0.5">
              <h2 className="font-extrabold text-4xl">
                Unable to access your attempt history currently
              </h2>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex p-2 gap-6">
          <div className="card w-72 card-xs shadow-sm border-1 border-base-200">
            <div className="card-body p-4 gap-0.5">
              <h2 className="font-medium text-base">Total Interviews Done</h2>
              <h2 className="font-extrabold text-4xl">
                {userAttemptHistory.length}
              </h2>
              <p className="font-medium">
                {
                  userAttemptHistory.filter(
                    (attempt) => attempt.difficulty === 'Easy'
                  ).length
                }{' '}
                Easy |{' '}
                {
                  userAttemptHistory.filter(
                    (attempt) => attempt.difficulty === 'Medium'
                  ).length
                }{' '}
                Medium |{' '}
                {
                  userAttemptHistory.filter(
                    (attempt) => attempt.difficulty === 'Hard'
                  ).length
                }{' '}
                Hard
              </p>
            </div>
          </div>

          <div className="card w-72 card-xs shadow-sm border-1 border-base-200">
            <div className="card-body p-4 gap-0.5">
              <h2 className="font-medium text-base">Total Time Spent</h2>
              <h2 className="font-extrabold text-4xl">
                {summariseTime(userAttemptHistory)}
              </h2>
            </div>
          </div>
        </div>
      )}

      {/* Recent Matches Table */}
      <p className="text-2xl p-2 font-light tracking-widest">
        Your recent matches
      </p>
      <div className="overflow-x-auto rounded-box shadow-sm border-1 border-base-200">
        <table className="table">
          {/* Table Head */}
          <thead>
            <tr>
              <th></th>
              <th>Category</th>
              <th>Difficulty</th>
              <th>Title</th>
              <th>Description</th>
              <th>Time Elapsed</th>
              <th>Attempted At</th>
              <th>Submitted Solution</th>
              <th>Sample Solution</th>
              <th>Feedback</th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody>
            {userAttemptHistory.map((e, i) => (
              <tr>
                <td className="font-semibold">{i + 1}</td>
                <td className="font-semibold">{e.category}</td>
                <td className="font-semibold">{e.difficulty}</td>
                <td className="font-semibold">{e.title}</td>
                <td className="font-semibold">{e.description}</td>
                <td className="font-semibold">{e.time_elapsed}</td>
                <td className="font-semibold">
                  {e.attempted_at.toLocaleString()}
                </td>
                <td className="font-semibold">{e.submitted_solution}</td>
                <td className="font-semibold">{e.solution_sample}</td>
                <td className="font-semibold">{e.feedback}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
