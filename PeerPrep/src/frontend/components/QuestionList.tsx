import QuestionItem from './QuestionItem';
import type { Question } from '../types/Question';
import React from 'react';

type Props = {
  questions: Question[];
};

/**
 * A formatted stack of questions with header.
 *
 * @param {Question[]} questions - Array of questions
 * @returns {React.FunctionComponent} Stack of questions
 */
const QuestionList: React.FC<Props> = ({ questions }) => {
  return (
    <>
      <div className="grid grid-cols-5 gap-4 p-4">
        <div className="font-bold">ID</div>
        <div className="font-bold">Title</div>
        <div className="font-bold">Difficulty</div>
        <div className="font-bold">Categories</div>
        <div className="font-bold">Actions</div>
      </div>
      <div className="join join-vertical">
        {questions.map((question, i) => (
          <QuestionItem
            key={question.id}
            question={question}
            color={i % 2 === 1 ? 'base-100' : 'base-200'}
          />
        ))}
      </div>
    </>
  );
};

export default QuestionList;
