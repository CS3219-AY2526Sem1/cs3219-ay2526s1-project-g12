import { apiClient } from './ApiClient';
import type { ApiResponse } from './ApiClient';
import type { User } from '../types/User.tsx';

type UserRegister = {
  readonly first_name: string;
  readonly last_name: string;
  readonly email: string;
  readonly password: string;
};

type UserUpdate = {
  readonly first_name?: string;
  readonly last_name?: string;
  readonly email?: string;
  readonly password?: string;
};

type UserResetPassword = {
  readonly token: string;
  readonly password: string;
};

type LoginResponse = {
  readonly access_token: string;
};

export const userApi = {
  /**
   * Makes a login request to the api.
   *
   * @param email
   * @param password
   * @returns ApiResponse with token data if successful.
   */
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

  /**
   * Makes a registration request to the api.
   *
   * @param {UserRegister} userData - The user registration data.
   * @returns {Promise<ApiResponse<User>>} ApiResponse with user data if successful.
   */
  async register(userData: UserRegister): Promise<ApiResponse<User>> {
    return apiClient.request('/us/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Logs out the current user by making a POST request to the logout endpoint.
   *
   * @returns {Promise<ApiResponse<null>>} ApiResponse indicating success or failure.
   */
  async logout(): Promise<ApiResponse<null>> {
    return apiClient.request('/auth/logout', {
      method: 'POST',
    });
  },

  /**
   * Fetches the current authenticated user's information from the API.
   *
   * @returns {Promise<ApiResponse<User>>} ApiResponse containing user data if successful.
   */
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return apiClient.request('/us/users/me');
  },

  /**
   * Update the current user's profile. Accepts a partial set of fields to update
   * and sends a PATCH request to the user service. Note that only the
   * authenticated user can update their own information (via the `/users/me` endpoint).
   *
   * @param {UserUpdate} updateData Partial user data to update.
   * @returns ApiResponse with updated user information if successful.
   */
  async updateUser(updateData: UserUpdate): Promise<ApiResponse<User>> {
    return apiClient.request('/us/users/me', {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  },

  /**
   * Request email verification by making a POST request to the verification token endpoint.
   *
   * @param email
   * @returns ApiResponse indicating success or failure.
   */
  async requestVerifyEmail(email: string): Promise<ApiResponse<null>> {
    return apiClient.request('/us/auth/request-verify-token', {
      method: 'POST',
      body: JSON.stringify({
        email: email,
      }),
    });
  },

  /**
   * Verify the user's email using the provided token by making a POST request to the verification endpoint.
   *
   * @param token
   * @returns ApiResponse with user data if successful.
   */
  async verifyEmail(token: string): Promise<ApiResponse<User>> {
    return apiClient.request('/us/auth/verify', {
      method: 'POST',
      body: JSON.stringify({
        token: token,
      }),
    });
  },

  /**
   * Request a password reset email by making a POST request to the forget-password endpoint.
   *
   * @param email
   * @returns ApiResponse indicating success or failure.
   */
  async forgotPassword(email: string): Promise<ApiResponse<null>> {
    return apiClient.request('/us/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({
        email: email,
      }),
    });
  },

  /**
   * Reset the user's password using the provided token and new password.
   *
   * @param data
   * @returns ApiResponse indicating success or failure.
   */
  async resetPassword(data: UserResetPassword): Promise<ApiResponse<null>> {
    return apiClient.request('/us/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Helper method to check if user is authenticated
  async checkAuth(): Promise<boolean> {
    const response = await this.getCurrentUser();
    return !response.error && !!response.data;
  },
};
