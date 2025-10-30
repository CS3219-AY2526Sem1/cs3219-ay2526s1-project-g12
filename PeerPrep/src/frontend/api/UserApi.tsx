import { apiClient } from './ApiClient';
import type { ApiResponse } from './ApiClient';

export const userApi = {
  // Auth
  async login(email: string, password: string): Promise<ApiResponse<any>> {
    console.log('Attempting login with:', email);

    return apiClient.request('/auth/login', {
      method: 'POST',
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
    return apiClient.request('/us/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  async logout(): Promise<ApiResponse<any>> {
    return apiClient.request('/auth/logout', {
      method: 'POST',
    });
  },

  async getCurrentUser(): Promise<ApiResponse<any>> {
    return apiClient.request('/us/users/me');
  },

  // Verify email with token
  async verifyEmail(token: string): Promise<ApiResponse<any>> {
    return apiClient.request('/us/auth/verify', {
      method: 'POST',
      body: JSON.stringify({
        token: token,
      }),
    });
  },

  // Helper method to check if user is authenticated
  async checkAuth(): Promise<boolean> {
    const response = await this.getCurrentUser();
    return !response.error && !!response.data;
  },
};
