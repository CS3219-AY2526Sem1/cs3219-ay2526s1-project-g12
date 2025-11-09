import React, { useEffect, useState } from 'react';
import { questionApi } from '../api/QuestionApi.tsx';
import type { Question } from '../types/Question.tsx';
import NavBar from '../components/NavBar.tsx';
import { NAV_BUTTONS } from '../config/NavConfig.tsx';
import { useNavigate } from 'react-router';

type SubmitState = {
  buttonText: string;
  allowSubmit: 'loading' | 'allow' | 'block';
  success: boolean;
};

function NewQuestion() {
  const [loading, setLoading] = useState<'loading' | 'success' | 'error'>(
    'success'
  );
  const [error, setError] = useState<string | null>(null);
  const [submission, setSubmission] = useState<SubmitState>({
    buttonText: 'Submit',
    allowSubmit: 'block',
    success: false,
  });
  const [newQuestionData, setNewQuestionData] = useState<Omit<Question, 'id'>>({
    title: '',
    description: '',
    difficulty: '',
    code_template: '',
    solution_sample: '',
    categories: [],
  });
  const [difficultyLevels, setDifficultyLevels] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading('loading');
    setError(null);

    const fetchDifficultyLevels = async () => {
      const res = await questionApi.getAllDifficulties();
      if (res.error) {
        setError('Failed to load difficulty levels.');
      } else if (res.data) {
        setDifficultyLevels(res.data.difficulties);
      }
    };

    const fetchCategories = async () => {
      const res = await questionApi.getAllCategories();
      if (res.error) {
        setError('Failed to load categories.');
      } else if (res.data) {
        setCategories(res.data.categories);
      }
    };

    fetchDifficultyLevels()
      .then(() => fetchCategories())
      .then(() => setLoading('success'));
  }, []);

  useEffect(() => {
    if (submission.success) {
      const timer = setTimeout(() => {
        navigate('/questions');
      }, 3000); // 3000 ms = 3 seconds

      return () => clearTimeout(timer); // cleanup in case component unmounts
    }
  }, [submission, navigate]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name } = e.target;

    // If it's a multi-select, collect all selected values
    if (e.target instanceof HTMLSelectElement && e.target.multiple) {
      const values = Array.from(e.target.selectedOptions).map((o) => o.value);
      setNewQuestionData((prev) => ({
        ...prev,
        [name]: values,
      }));
    } else {
      const { value } = e.target;
      setNewQuestionData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }

    // Clear error when user starts typing
    if (error) setError(null);
    setSubmission((prev) => ({
      ...prev,
      buttonText: 'Submit',
      allowSubmit: 'allow',
    }));
  };

  const handleSubmit = async () => {
    setSubmission((prev) => ({
      ...prev,
      buttonText: 'Submitting...',
      allowSubmit: 'loading',
    }));
    if (
      !newQuestionData.title ||
      !newQuestionData.description ||
      !newQuestionData.difficulty ||
      !newQuestionData.code_template ||
      !newQuestionData.solution_sample ||
      newQuestionData.categories.length === 0
    ) {
      setError('Fields cannot be empty!');
      setSubmission((prev) => ({
        ...prev,
        buttonText: 'Submit',
        allowSubmit: 'block',
      }));
      return;
    }

    const { error } = await questionApi.createQuestion(newQuestionData);
    if (error) {
      setError(error);
      setSubmission((prev) => ({
        ...prev,
        buttonText: 'Submit',
        allowSubmit: 'block',
      }));
    } else {
      setSubmission({
        buttonText: 'Submitted',
        allowSubmit: 'block',
        success: true,
      });
    }
  };

  return (
    <div className="min-h-screen px-20 py-10">
      <NavBar buttons={NAV_BUTTONS} />
      <h1 className="text-6xl font-semibold p-2">New Question</h1>
      <main>
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {submission.success && (
            <div className="alert alert-success alert-soft mb-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 shrink-0 stroke-current"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>
                Question created! Redirecting back to admin page in 3 seconds...
              </span>
            </div>
          )}
          {error && (
            <div className="alert alert-error alert-soft mb-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 shrink-0 stroke-current"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{error}</span>
            </div>
          )}
          {loading === 'loading' ? (
            <div className="flex justify-center py-10">
              <span className="loading loading-dots loading-xl" />
              <p className="ml-4 mt-2">
                {' '}
                Fetching categories and difficulties...
              </p>
            </div>
          ) : (
            <>
              <fieldset className="px-2">
                <label htmlFor="title" className="fieldset-legend font-normal">
                  Title
                </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  required
                  className="input validator w-full"
                  placeholder="Title"
                  value={newQuestionData.title}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label
                  htmlFor="description"
                  className="fieldset-legend font-normal"
                >
                  Description
                </label>
                <textarea
                  id="description"
                  name="description"
                  required
                  className="textarea h-40 validator w-full"
                  placeholder="Description"
                  value={newQuestionData.description}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label
                  htmlFor="difficulty"
                  className="fieldset-legend font-normal"
                >
                  Difficulty
                </label>
                <select
                  id="difficulty"
                  name="difficulty"
                  required
                  className="select w-full"
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                >
                  <option disabled selected>
                    Choose a level
                  </option>
                  {difficultyLevels.map((level) => (
                    <option
                      key={level}
                      value={level}
                      selected={newQuestionData.difficulty === level}
                    >
                      {level}
                    </option>
                  ))}
                </select>
                <label
                  htmlFor="code_template"
                  className="fieldset-legend font-normal"
                >
                  Code template
                </label>
                <textarea
                  id="code_template"
                  name="code_template"
                  required
                  className="textarea h-40 validator w-full"
                  placeholder="Code template"
                  value={newQuestionData.code_template}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label
                  htmlFor="solution_sample"
                  className="fieldset-legend font-normal"
                >
                  Sample solution
                </label>
                <textarea
                  id="solution_sample"
                  name="solution_sample"
                  required
                  className="textarea h-40 validator w-full"
                  placeholder="Sample solution"
                  value={newQuestionData.solution_sample}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label
                  htmlFor="categories"
                  className="fieldset-legend font-normal"
                >
                  Categories
                </label>
                <select
                  id="categories"
                  name="categories"
                  required
                  className="select h-60 w-full"
                  multiple
                  value={newQuestionData.categories}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                >
                  <option disabled>
                    Hold ctrl/cmd to select multiple categories
                  </option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </fieldset>
              {/* Save & Cancel */}
              <div className="flex flex-col md:flex-row gap-4 mt-6 px-2">
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleSubmit}
                  disabled={
                    submission.allowSubmit !== 'allow' || submission.success
                  }
                >
                  {submission.buttonText}
                </button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default NewQuestion;
