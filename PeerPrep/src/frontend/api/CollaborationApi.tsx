import { apiClient } from './ApiClient';
import type { ApiResponse } from './ApiClient';

interface CollabResponse {
  message: string;
}

interface CollabQnResponse {
    message: {
        title: string;
        description: string;
        code_template: string;
        solution_sample: string;
        difficulty: string;
        category: string;
    }
}

export const collabApi = {
  async connect(matchId: string): Promise<ApiResponse<CollabQnResponse>> {
    return apiClient.request(`/cs/connect/${matchId}`, {
      method: 'GET',
    });
  },

  async reconnect(): Promise<ApiResponse<CollabResponse>> {
    return apiClient.request('/cs/reconnect', {
      method: 'POST',
    });
  },

  async terminate(
    userId: string,
    matchId: string,
    code: string
  ): Promise<ApiResponse<CollabResponse>> {
    return apiClient.request(`/cs/terminate/${matchId}`, {
      method: 'POST',
      body: JSON.stringify({
        data: {
          user_id: userId,
          match_id: matchId,
          message: 'terminate',
          code: code,
        },
      }),
    });
  },
};
