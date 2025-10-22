import { ApiClient } from "./ApiClient";
import type { ApiResponse } from "./ApiClient";

// Separate ApiClient instance for Question Service (Temporary)
const qnApiClient = new ApiClient("http://localhost:8002");

export interface Question {
  title: string;
  description: string;
  difficulty: string;
  code_template: string;
  solution_sample: string;
  categories: Array<string>;
}

export interface PoolQuestion extends Question {
  id: number;
}

export interface Category {
  name: string;
}

export interface Difficulty {
  level: string;
}

export const questionApi = {
  // ------------------ QUESTIONS ------------------

  async getAllQuestions(
    userId: string,
    start: number = 1,
    end: number = 10,
  ): Promise<ApiResponse<Question[]>> {
    return qnApiClient.request(`/questions/?start=${start}&end=${end}`, {
      method: "GET",
      headers: { "X-User-ID": userId },
    });
  },

  async getQuestionById(
    userId: string,
    questionId: number,
  ): Promise<ApiResponse<Question>> {
    return qnApiClient.request(`/questions/${questionId}`, {
      method: "GET",
      headers: { "X-User-ID": userId },
    });
  },

  async createQuestion(
    userId: string,
    data: Question,
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request("/questions/", {
      method: "POST",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  async updateQuestion(
    userId: string,
    questionId: number,
    data: Partial<Question>,
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request(`/questions/${questionId}`, {
      method: "PUT",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  async deleteQuestion(
    userId: string,
    questionId: number,
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request(`/questions/${questionId}`, {
      method: "DELETE",
      headers: { "X-User-ID": userId },
    });
  },

  // ------------------ CATEGORY ------------------

  async getAllCategories(
    userId: string,
  ): Promise<ApiResponse<{ categories: string[] }>> {
    return qnApiClient.request("/category/", {
      method: "GET",
      headers: { "X-User-ID": userId },
    });
  },

  async createCategory(
    userId: string,
    data: Category,
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request("/category/", {
      method: "POST",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  async updateCategory(
    userId: string,
    data: { name: string; new_name: string },
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request(`/category/`, {
      method: "PUT",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  async deleteCategory(
    userId: string,
    data: Category,
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request(`/category/`, {
      method: "DELETE",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  // ------------------ DIFFICULTY ------------------

  async getAllDifficulties(
    userId: string,
  ): Promise<ApiResponse<{ difficulties: string[] }>> {
    return qnApiClient.request("/difficulty/", {
      method: "GET",
      headers: { "X-User-ID": userId },
    });
  },

  async createDifficulty(
    userId: string,
    data: Difficulty,
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request("/difficulty/", {
      method: "POST",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  async updateDifficulty(
    userId: string,
    data: { level: string; new_level: string },
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request(`/difficulty/`, {
      method: "PUT",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  async deleteDifficulty(
    userId: string,
    data: Difficulty,
  ): Promise<ApiResponse<{ message: string }>> {
    return qnApiClient.request(`/difficulty/`, {
      method: "DELETE",
      headers: { "X-User-ID": userId },
      body: JSON.stringify(data),
    });
  },

  // ------------------ POOL ------------------
  async getPoolCategories(
    userId: string,
  ): Promise<ApiResponse<{ categories: string[] }>> {
    return qnApiClient.request("/pool/category/", {
      method: "GET",
      headers: { "X-User-ID": userId },
    });
  },

  async getPoolDifficultiesByCategory(
    userId: string,
    category: string,
  ): Promise<ApiResponse<{ difficulty_levels: string[] }>> {
    return qnApiClient.request(
      `/pool/${encodeURIComponent(category)}/difficulty/`,
      {
        method: "GET",
        headers: { "X-User-ID": userId },
      },
    );
  },

  async getRandomQuestionFromPool(
    userId: string,
    category: string,
    difficulty: string,
  ): Promise<ApiResponse<PoolQuestion>> {
    return qnApiClient.request(
      `/pool/${encodeURIComponent(category)}/${encodeURIComponent(difficulty)}/`,
      {
        method: "GET",
        headers: { "X-User-ID": userId },
      },
    );
  },
};
