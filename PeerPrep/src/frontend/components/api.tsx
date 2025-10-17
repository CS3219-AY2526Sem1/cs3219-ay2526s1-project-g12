const API_URL = 'http://localhost:8000';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        credentials: 'include', // for cookie-based auth
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      // Handle 204 No Content response
      if (response.status === 204) {
        return { data: null as unknown as T };
      }

      const text = await response.text();
      if (!response.ok) {
        // Try to parse JSON error, else return text
        let errMsg: string;
        try {
          const json = JSON.parse(text);
          errMsg = json.detail || JSON.stringify(json);
        } catch {
          errMsg = text || `HTTP ${response.status}`;
        }
        return { error: errMsg };
      }

      const data = text ? JSON.parse(text) : null;
      return { data };
    } catch (err) {
      return { error: err instanceof Error ? err.message : 'Unknown error' };
    }
  }

  // Auth
  async login(email: string, password: string): Promise<ApiResponse<any>> {
    console.log('Attempting login with:', email);

    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username: email,
        password: password,
      }),
    });
  }


  async register(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }): Promise<ApiResponse<any>> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout(): Promise<ApiResponse<any>> {
    return this.request('/auth/logout', {
      method: 'POST',
    });
  }

  async getCurrentUser(): Promise<ApiResponse<any>> {
    return this.request('/users/me');
  }

  async getProtectedData(): Promise<ApiResponse<string>> {
    return this.request('/protected-route');
  }

  // Helper method to check if user is authenticated
  async checkAuth(): Promise<boolean> {
    const response = await this.getCurrentUser();
    return !response.error && !!response.data;
  }
}

export const apiClient = new ApiClient(API_URL);
