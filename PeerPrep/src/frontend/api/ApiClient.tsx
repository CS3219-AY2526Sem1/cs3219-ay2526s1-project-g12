export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        credentials: "include", // for cookie-based auth
        headers: {
          "Content-Type": "application/json",
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
      return { error: err instanceof Error ? err.message : "Unknown error" };
    }
  }

  async getProtectedData(): Promise<ApiResponse<string>> {
    return this.request("/protected-route");
  }
}

// Singleton instance (shared across services)
export const apiClient = new ApiClient("http://localhost:8000");
