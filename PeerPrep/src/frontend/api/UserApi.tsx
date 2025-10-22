import { apiClient } from "./ApiClient";
import type { ApiResponse } from "./ApiClient";

export const userApi = {
  // Auth
  async login(email: string, password: string): Promise<ApiResponse<any>> {
    console.log("Attempting login with:", email);

    return apiClient.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: email,
        password: password,
      }),
    });
  },

  async register(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }): Promise<ApiResponse<any>> {
    return apiClient.request("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  async logout(): Promise<ApiResponse<any>> {
    return apiClient.request("/auth/logout", {
      method: "POST",
    });
  },

  async getCurrentUser(): Promise<ApiResponse<any>> {
    return apiClient.request("/users/me");
  },

  // Helper method to check if user is authenticated
  async checkAuth(): Promise<boolean> {
    const response = await this.getCurrentUser();
    return !response.error && !!response.data;
  },
};
