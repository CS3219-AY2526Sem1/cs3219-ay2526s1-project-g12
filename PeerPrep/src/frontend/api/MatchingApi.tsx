import { apiClient } from './ApiClient';
import type { ApiResponse } from './ApiClient';

export interface MatchRequest {
  user_id: string;
  category: string;
  difficulty: string;
}

export interface MatchConfirmRequest {
  user_id: string;
}

export interface ConfirmMatchSuccess {
  message: string;
  match_details?: string;
}

export const matchingApi = {
  async getRootStatus(): Promise<ApiResponse<{ status: string }>> {
    return apiClient.request('/ms', { method: 'GET' });
  },

  async checkQueueConnection(): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request('/ms/check_connection/queue', {
      method: 'GET',
    });
  },

  async checkMessageQueueConnection(): Promise<
    ApiResponse<{ message: string }>
  > {
    return apiClient.request('/ms/check_connection/message_queue', {
      method: 'GET',
    });
  },

  async findMatch(matchRequest: MatchRequest): Promise<ApiResponse<any>> {
    return apiClient.request('/ms/find_match', {
      method: 'POST',
      body: JSON.stringify(matchRequest),
    });
  },

  async terminateMatch(cancelRequest: MatchRequest): Promise<ApiResponse<any>> {
    return apiClient.request('/ms/terminate_match', {
      method: 'DELETE',
      body: JSON.stringify(cancelRequest),
    });
  },

  async confirmMatch(
    matchId: string,
    confirmRequest: MatchConfirmRequest
  ): Promise<ApiResponse<ConfirmMatchSuccess>> {
    return apiClient.request(`/ms/confirm_match/${matchId}`, {
      method: 'POST',
      body: JSON.stringify(confirmRequest),
    });
  },
};
