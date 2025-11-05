/**
 * Interface representing a question object.
 */
export interface Question {
  /** Unique identifier for the question */
  readonly id: number;
  /** Title of the question */
  readonly title: string;
  /** Description of the question */
  readonly description: string;
  /** Difficulty level of the question */
  readonly difficulty: string;
  /** Code template provided for the question */
  readonly code_template: string;
  /** Sample solution for the question */
  readonly solution_sample: boolean;
  /** Categories associated with the question */
  readonly categories: string[];
}
