import { useEffect, useState } from 'react';
import NavBar from '../components/NavBar';
import { NAV_BUTTONS } from '../config/NavConfig';
import { useAuth } from '../context/AuthContext';
import {
  questionHistoryApi,
  type QuestionHistory,
} from '../api/QuestionHistoryApi';
import Markdown from 'react-markdown';

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

  const summariseTotalTime = (uah: QuestionHistory[]) => {
    const totalTime: number = uah
      .map((attempt) => attempt.time_elapsed)
      .reduce((a, b) => a + b, 0);
    return formatDuration(totalTime);
  };

  const formatDuration = (duration: number) => {
    const hours = duration / 60 / 60;
    const minutes = (duration / 60) % 60;
    return `${hours.toFixed(0)}h ${minutes.toFixed(0)}m`;
  };

  const formatDate = (date: string) => {
    const d = new Date(date);
    return d.toLocaleString();
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
          <div className="stats stats-vertical lg:stats-horizontal shadow-md border-1 border-base-200">
            <div className="stat">
              <div className="stat-value">
                <span className="loading loading-spinner loading-xl"></span>
              </div>
            </div>
          </div>
        </div>
      ) : error ? (
        <div className="flex p-2 gap-6">
          <div className="stats stats-vertical lg:stats-horizontal shadow-md border-1 border-base-200">
            <div className="stat">
              <div className="stat-title text-lg">
                <div className="badge badge-error">Error</div>
              </div>
              <div className="stat-value">
                Unable to access your attempt history currently
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex p-2 gap-6">
          <div className="stats stats-vertical lg:stats-horizontal shadow-md border-1 border-base-200">
            <div className="stat">
              <div className="stat-title text-lg">
                Total Interviews Completed
              </div>
              <div className="stat-value"> {userAttemptHistory.length}</div>
              <div className="stat-desc">
                <div className="badge badge-soft badge-success m-0.5">
                  {
                    userAttemptHistory.filter(
                      (attempt) => attempt.difficulty === 'Easy'
                    ).length
                  }{' '}
                  Easy
                </div>
                <div className="badge badge-soft badge-warning m-0.5">
                  {
                    userAttemptHistory.filter(
                      (attempt) => attempt.difficulty === 'Medium'
                    ).length
                  }{' '}
                  Medium
                </div>
                <div className="badge badge-soft badge-error m-0.5">
                  {
                    userAttemptHistory.filter(
                      (attempt) => attempt.difficulty === 'Hard'
                    ).length
                  }{' '}
                  Hard
                </div>
              </div>
            </div>

            <div className="stat">
              <div className="stat-title text-lg">Total Time Spent</div>
              <div className="stat-value">
                {summariseTotalTime(userAttemptHistory)}
              </div>
              <div className="stat-desc">&nbsp;</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Matches Table */}
      <p className="text-2xl p-2 font-light tracking-widest">
        Your recent matches
      </p>
      <div className="overflow-x-auto rounded-box shadow-md border-1 border-base-200">
        <div className="join join-vertical bg-base-100 w-full">
          <div className="collapse collapse-arrow join-item border-base-300 border">
            <input type="radio" name="my-accordion-4" defaultChecked />
            <div className="collapse-title font-semibold">Attempts</div>
            <div className="collapse-content text-sm">
              View the list of your recent matches below.
            </div>
          </div>
          {userAttemptHistory.map((e, i) => (
            <div className="collapse collapse-arrow join-item border-base-300 border">
              <input type="radio" name="my-accordion-4" />
              <div className="collapse-title">
                <p className="font-semibold text-lg">
                  {i + 1}.{e.title}
                </p>
                <pre>
                  Category: {e.category} | Difficulty: {e.difficulty}
                </pre>
                <pre>
                  Time Taken: {formatDuration(e.time_elapsed)} | Attempted at:{' '}
                  {formatDate(e.attempted_at)}
                </pre>
              </div>
              <div className="collapse-content m-2">
                <div className="pt-1 pb-1">
                  <div className="badge badge-outline mb-1">
                    <pre className="text-base">Submitted Solution</pre>
                  </div>
                  <div className="mockup-code w-full bg-gray-800 text-white">
                    {e.submitted_solution.split('\n').map((line, index) => (
                      <pre data-prefix={index + 1}>
                        <code>{line}</code>
                      </pre>
                    ))}
                  </div>
                </div>
                <div className="pt-1 pb-1">
                  <div className="badge badge-outline mb-1">
                    <pre className="text-base">Sample Solution</pre>
                  </div>
                  <div className="mockup-code w-full  bg-gray-800 text-white">
                    {e.solution_sample.split('\n').map((line, index) => (
                      <pre data-prefix={index + 1}>
                        <code>{line}</code>
                      </pre>
                    ))}
                  </div>
                </div>
                <div className="pt-1 pb-1">
                  <div className="badge badge-outline mb-1">
                    <pre className="text-base">AI Assisted Feedback</pre>
                  </div>
                  <div className="mockup-window border border-base-300 w-full">
                    <div className="grid place-content-center border-t border-base-300 h-auto p-3">
                      <Markdown>{e.feedback}</Markdown>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
