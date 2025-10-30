import { apiClient } from './ApiClient';
import type { ApiResponse } from './ApiClient';
import type { User } from '../types/User.tsx';

type UserRegister = {
  readonly first_name: string;
  readonly last_name: string;
  readonly email: string;
  readonly password: string;
};

type LoginResponse = {
  readonly access_token: string;
};

export const userApi = {
  // Auth
  async login(
    email: string,
    password: string
  ): Promise<ApiResponse<LoginResponse>> {
    console.log('Attempting login with:', email);

    return apiClient.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username: email,
        password: password,
      }),
    });
  },

  async register(userData: UserRegister): Promise<ApiResponse<User>> {
    return apiClient.request('/us/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  async logout(): Promise<ApiResponse<null>> {
    return apiClient.request('/auth/logout', {
      method: 'POST',
    });
  },

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return apiClient.request('/us/users/me');
  },

  // Verify email with token
  async verifyEmail(token: string): Promise<ApiResponse<User>> {
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
