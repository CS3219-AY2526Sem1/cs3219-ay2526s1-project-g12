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
import { useEffect, useMemo, useState } from 'react';
import { questionApi, type QuestionsResponse } from '../api/QuestionApi.tsx';
import { useSearchParams } from 'react-router';

const TOTAL_QUESTIONS = 2641;

function Questions() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [questions, setQuestions] = useState<QuestionsResponse>({
    questions: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Defaults
  const pageParam = parseInt(searchParams.get('page') || '1', 10);
  const pageSizeParam = parseInt(searchParams.get('pageSize') || '20', 10);

  // Clamp to sensible bounds
  const pageSize =
    Number.isFinite(pageSizeParam) && pageSizeParam > 0 ? pageSizeParam : 20;
  const page = Number.isFinite(pageParam) && pageParam > 0 ? pageParam : 1;

  const { start, end } = useMemo(() => {
    const s = (page - 1) * pageSize + 1;
    const e = page * pageSize;
    return { start: s, end: e };
  }, [page, pageSize]);

  useEffect(() => {
    const nextParams = new URLSearchParams(searchParams);
    if (!searchParams.has('page')) nextParams.set('page', String(page));
    if (!searchParams.has('pageSize'))
      nextParams.set('pageSize', String(pageSize));
    if (nextParams.toString() !== searchParams.toString()) {
      setSearchParams(nextParams);
      return;
    }

    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await questionApi.getAllQuestions(start, end);
        if (cancelled) return;

        if (res.error) {
          setError('Failed to load questions.');
        } else if (res.data) {
          setQuestions(res.data);
        }
      } catch {
        if (!cancelled) setError('Failed to load questions.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [page, pageSize]);

  const totalPages = Math.max(1, Math.ceil(TOTAL_QUESTIONS / pageSize));

  const canPrev = page > 1;
  const canNext = page < totalPages;

  const goTo = (nextPage: number) => {
    const next = Math.max(1, Math.min(nextPage, totalPages));
    setSearchParams({
      page: String(next),
      pageSize: String(pageSize),
    });
  };

  const changePageSize = (size: number) => {
    // Reset to page 1 on page size change
    setSearchParams({
      page: '1',
      pageSize: String(size),
    });
  };

  // Build a short window of page numbers (if we know total)
  const pageWindow = useMemo(() => {
    if (!totalPages) return [];
    const span = 5; // show up to 5 buttons
    const half = Math.floor(span / 2);
    let startPage = Math.max(1, page - half);
    const endPage = Math.min(totalPages, startPage + span - 1);
    startPage = Math.max(1, endPage - span + 1);
    return Array.from(
      { length: endPage - startPage + 1 },
      (_, i) => startPage + i
    );
  }, [page, totalPages]);

  const showingStart = start;
  const showingEnd = Math.min(end, TOTAL_QUESTIONS);

  return (
    <div className="min-h-screen px-20 py-10">
      <NavBar buttons={NAV_BUTTONS} />
      <h1 className="text-6xl font-semibold p-2">Questions administration</h1>
      <main>
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {/* Top toolbar */}
          <div className="flex items-center justify-between gap-4">
            <div className="text-sm opacity-70">
              Showing <b>{showingStart}</b>–<b>{showingEnd}</b> of{' '}
              <b>{TOTAL_QUESTIONS}</b>
            </div>

            <div className="flex items-center gap-3">
              <label className="label">
                <span className="label-text">Page size</span>
              </label>
              <select
                className="select select-bordered select-sm"
                value={pageSize}
                onChange={(e) => changePageSize(parseInt(e.target.value, 10))}
              >
                {[10, 20, 50, 100].map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Content */}
          {loading ? (
            <span className="loading loading-dots loading-xl"></span>
          ) : error ? (
            <div className="alert alert-error alert-soft">
              <span>{error}</span>
            </div>
          ) : (
            <QuestionList questions={questions.questions} />
          )}
          {/* Pagination controls */}
          <div className="flex items-center justify-between pt-4">
            <div className="join">
              <button
                className="btn join-item"
                onClick={() => goTo(1)}
                disabled={!canPrev}
              >
                « First
              </button>
              <button
                className="btn join-item"
                onClick={() => goTo(page - 1)}
                disabled={!canPrev}
              >
                ‹ Prev
              </button>
            </div>

            {/* Numbered pages */}
            {totalPages && (
              <div className="join hidden sm:inline-flex">
                {pageWindow.map((pn) => (
                  <button
                    key={pn}
                    className={`btn join-item ${pn === page ? 'btn-active' : ''}`}
                    onClick={() => goTo(pn)}
                  >
                    {pn}
                  </button>
                ))}
              </div>
            )}

            <div className="join">
              <button
                className="btn join-item"
                onClick={() => goTo(page + 1)}
                disabled={!canNext}
              >
                Next ›
              </button>
              {totalPages && (
                <button
                  className="btn join-item"
                  onClick={() => goTo(totalPages)}
                  disabled={!canNext}
                >
                  Last »
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Questions;
