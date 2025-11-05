/**
 * Questions Administration Page
 *
 * This component renders the Questions Administration page, including a navigation bar
 * and a list of questions. It uses the NavBar component for navigation and the QuestionList
 * component to display the questions.
 */
import NavBar from '../components/NavBar';
import { NAV_BUTTONS } from '../config/NavConfig';
import QuestionList from '../components/QuestionList.tsx';
import { useEffect, useState } from 'react';
import { questionApi, type QuestionsResponse } from '../api/QuestionApi.tsx';

function Questions() {
  const [questions, setQuestions] = useState<QuestionsResponse>({
    questions: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const fetchQuestions = async () => {
      const res = await questionApi.getAllQuestions();
      if (res.error) {
        setError('Failed to load questions.');
      } else if (res.data) {
        setQuestions(res.data);
      }
      setLoading(false);
    };
    fetchQuestions();
  }, []);
  return (
    <div className="min-h-screen px-20 py-10">
      <NavBar buttons={NAV_BUTTONS} />
      <h1 className="text-6xl font-semibold p-2">Questions administration</h1>
      <main>
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {loading ? (
            <span className="loading loading-dots loading-xl"></span>
          ) : error ? (
            <div className="alert alert-error alert-soft">
              <span>{error}</span>
            </div>
          ) : (
            <QuestionList questions={questions.questions} />
          )}
        </div>
      </main>
    </div>
  );
}

export default Questions;
