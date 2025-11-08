import { useSearchParams } from 'react-router';
import React, { useEffect, useState } from 'react';
import { questionApi } from '../api/QuestionApi.tsx';
import type { Question } from '../types/Question.tsx';
import NavBar from '../components/NavBar.tsx';
import { NAV_BUTTONS } from '../config/NavConfig.tsx';
import type { Mutable } from '../types/Mutable.tsx';

type SubmitState = {
  buttonText: string;
  allowSubmit: 'loading' | 'allow' | 'block';
  success: boolean;
};

const arraysHaveSameElements = <T,>(arr1: T[], arr2: T[]): boolean => {
  if (arr1.length !== arr2.length) return false;
  const sorted1 = [...arr1].sort();
  const sorted2 = [...arr2].sort();
  return JSON.stringify(sorted1) === JSON.stringify(sorted2);
};

function EditQuestion() {
  const [searchParams] = useSearchParams();
  const questionId = searchParams.get('id');
  let questionIdNum: number = 0;

  const [loading, setLoading] = useState<'loading' | 'success' | 'error'>(
    'success'
  );
  const [error, setError] = useState<string | null>(null);
  const [submission, setSubmission] = useState<SubmitState>({
    buttonText: 'Save changes',
    allowSubmit: 'block',
    success: false,
  });
  const [questionData, setQuestionData] = useState<Question>();
  const [difficultyLevels, setDifficultyLevels] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [updateQuestion, setUpdateQuestion] = useState<Omit<Question, 'id'>>({
    title: '',
    description: '',
    difficulty: '',
    code_template: '',
    solution_sample: '',
    categories: [],
  });

  useEffect(() => {
    setLoading('loading');
    setError(null);
    // Cast questionId to number
    if (!questionId) {
      setError('No question ID provided in the URL.');
      setLoading('error');
      return;
    } else {
      questionIdNum = Number(questionId);
      if (isNaN(questionIdNum)) {
        setError('Invalid question ID provided in the URL.');
        setLoading('error');
        return;
      }
    }

    /**
     * Fetch question details on mount
     */
    const fetchQuestion = async () => {
      // Fetch question details using questionId
      const res = await questionApi.getQuestionById(questionIdNum);
      if (res.error) {
        setError('Failed to load question.');
      } else if (res.data) {
        setQuestionData(res.data);
        setUpdateQuestion(res.data);
      }
    };

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

    fetchQuestion()
      .then(() => fetchDifficultyLevels())
      .then(() => fetchCategories())
      .then(() => setLoading('success'));
  }, [questionId]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name } = e.target;

    // If it's a multi-select, collect all selected values
    if (e.target instanceof HTMLSelectElement && e.target.multiple) {
      const values = Array.from(e.target.selectedOptions).map((o) => o.value);
      setUpdateQuestion((prev) => ({
        ...prev,
        [name]: values,
      }));
    } else {
      const { value } = e.target;
      setUpdateQuestion((prev) => ({
        ...prev,
        [name]: value,
      }));
    }

    // Clear error when user starts typing
    if (error) setError(null);
    setSubmission({
      buttonText: 'Save changes',
      allowSubmit: 'allow',
      success: false,
    });
  };

  const handleCancel = () => {
    if (questionData) {
      setUpdateQuestion(questionData);
    }
    setSubmission({
      buttonText: 'Save changes',
      allowSubmit: 'block',
      success: false,
    });
    setError(null);
  };

  const handleSave = async () => {
    if (!questionData) return;
    setSubmission({
      buttonText: 'Saving...',
      allowSubmit: 'loading',
      success: false,
    });
    if (
      !updateQuestion.title ||
      !updateQuestion.description ||
      !updateQuestion.difficulty ||
      !updateQuestion.code_template ||
      !updateQuestion.solution_sample ||
      updateQuestion.categories.length === 0
    ) {
      setError('Fields cannot be empty!');
      setSubmission({
        buttonText: 'Save changes',
        allowSubmit: 'block',
        success: false,
      });
      return;
    }
    const updateData: Partial<Mutable<Question>> = {};
    if (updateQuestion.title !== questionData.title)
      updateData.title = updateQuestion.title;
    if (updateQuestion.description !== questionData.description)
      updateData.description = updateQuestion.description;
    if (updateQuestion.difficulty !== questionData.difficulty)
      updateData.difficulty = updateQuestion.difficulty;
    if (updateQuestion.code_template !== questionData.code_template)
      updateData.code_template = updateQuestion.code_template;
    if (updateQuestion.solution_sample !== questionData.solution_sample)
      updateData.solution_sample = updateQuestion.solution_sample;
    if (
      !arraysHaveSameElements(
        updateQuestion.categories,
        questionData.categories
      )
    )
      updateData.categories = updateQuestion.categories;

    if (Object.keys(updateData).length === 0) {
      setError('No changes to save.');
      setSubmission({
        buttonText: 'Save changes',
        allowSubmit: 'block',
        success: false,
      });
      return;
    }

    const { error } = await questionApi.updateQuestion(
      questionData.id,
      updateData
    );
    if (error) {
      setError(error);
      setSubmission({
        buttonText: 'Save changes',
        allowSubmit: 'block',
        success: false,
      });
    } else {
      setSubmission({
        buttonText: 'Save changes',
        allowSubmit: 'block',
        success: true,
      });
    }
  };

  return (
    <div className="min-h-screen px-20 py-10">
      <NavBar buttons={NAV_BUTTONS} />
      <h1 className="text-6xl font-semibold p-2">Edit Question</h1>
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
              <span>Question updated!</span>
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
            <>
              <span className="loading loading-dots loading-xl"></span>
              <p className="mt-4">Loading question data...</p>
            </>
          ) : (
            <>
              <fieldset className="px-2">
                <label htmlFor="title" className="label font-normal">
                  Title
                </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  required
                  className="input validator w-full"
                  placeholder="Title"
                  value={updateQuestion.title}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label htmlFor="description" className="label font-normal">
                  Description
                </label>
                <textarea
                  id="description"
                  name="description"
                  required
                  className="textarea h-40 validator w-full"
                  placeholder="Description"
                  value={updateQuestion.description}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label htmlFor="difficulty" className="label font-normal">
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
                  <option disabled>Choose a level</option>
                  {difficultyLevels.map((level) => (
                    <option
                      key={level}
                      value={level}
                      selected={updateQuestion.difficulty === level}
                    >
                      {level}
                    </option>
                  ))}
                </select>
                <label htmlFor="code_template" className="label font-normal">
                  Code template
                </label>
                <textarea
                  id="code_template"
                  name="code_template"
                  required
                  className="textarea h-40 validator w-full"
                  placeholder="Code template"
                  value={updateQuestion.code_template}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label htmlFor="solution_sample" className="label font-normal">
                  Sample solution
                </label>
                <textarea
                  id="solution_sample"
                  name="solution_sample"
                  required
                  className="textarea h-40 validator w-full"
                  placeholder="Sample solution"
                  value={updateQuestion.solution_sample}
                  onChange={handleInputChange}
                  disabled={submission.allowSubmit === 'loading'}
                />
                <label htmlFor="categories" className="label font-normal">
                  Categories
                </label>
                <select
                  id="categories"
                  name="categories"
                  required
                  className="select h-60 w-full"
                  multiple
                  value={updateQuestion.categories}
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
                  onClick={handleSave}
                  disabled={submission.allowSubmit !== 'allow'}
                >
                  {submission.buttonText}
                </button>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={handleCancel}
                >
                  Cancel
                </button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default EditQuestion;
