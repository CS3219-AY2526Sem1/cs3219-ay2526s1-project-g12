import { apiClient } from './ApiClient';
import type { ApiResponse } from './ApiClient';

export interface QuestionHistory {
  id: number;
  title: string;
  description: string;
  code_template: string;
  solution_sample: string;
  difficulty: string;
  category: string;
  time_elapsed: number;
  submitted_solution: string;
  attempted_at: Date;
  feedback: string;
}

export const questionHistoryApi = {
  async getRootStatus(): Promise<ApiResponse<{ status: string }>> {
    return apiClient.request('/qhs', { method: 'GET' });
  },

  async get_question_history_details_by_user_id(): Promise<
    ApiResponse<QuestionHistory[]>
  > {
    return apiClient.request('/qhs/attempts', {
      method: 'GET',
    });
  },
};
