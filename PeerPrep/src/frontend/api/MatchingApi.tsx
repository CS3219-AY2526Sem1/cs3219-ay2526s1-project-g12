import { ApiClient } from "./ApiClient";
import type { ApiResponse } from "./ApiClient";

// Separate ApiClient instance for Matching Service (Temporary)
const matchingApiClient = new ApiClient("http://localhost:8003");

export interface MatchRequest {
  user_id: string;
  category: string;
  difficulty: string;
}

export interface MatchConfirmRequest {
  user_id: string;
}

export const matchingApi = {
  async getRootStatus(): Promise<ApiResponse<{ status: string }>> {
    return matchingApiClient.request("/", { method: "GET" });
  },

  async checkQueueConnection(): Promise<ApiResponse<{ message: string }>> {
    return matchingApiClient.request("/check_connection/queue", {
      method: "GET",
    });
  },

  async checkMessageQueueConnection(): Promise<
    ApiResponse<{ message: string }>
  > {
    return matchingApiClient.request("/check_connection/message_queue", {
      method: "GET",
    });
  },

  async findMatch(matchRequest: MatchRequest): Promise<ApiResponse<any>> {
    return matchingApiClient.request("/find_match", {
      method: "POST",
      body: JSON.stringify(matchRequest),
    });
  },

  async terminateMatch(cancelRequest: MatchRequest): Promise<ApiResponse<any>> {
    return matchingApiClient.request("/terminate_match", {
      method: "DELETE",
      body: JSON.stringify(cancelRequest),
    });
  },

  async confirmMatch(
    matchId: string,
    confirmRequest: MatchConfirmRequest,
  ): Promise<ApiResponse<any>> {
    return matchingApiClient.request(`/confirm_match/${matchId}`, {
      method: "POST",
      body: JSON.stringify(confirmRequest),
    });
  },
};
