import { apiClient } from './ApiClient';
import type { ApiResponse } from './ApiClient';
import type { Question } from '../types/Question.tsx';

export interface QuestionsResponse {
  questions: Question[];
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
    start: number = 1,
    end: number = 10
  ): Promise<ApiResponse<QuestionsResponse>> {
    return apiClient.request(`/qs/questions/?start=${start}&end=${end}`, {
      method: 'GET',
    });
  },

  async getQuestionById(questionId: number): Promise<ApiResponse<Question>> {
    return apiClient.request(`/qs/questions/${questionId}`, {
      method: 'GET',
    });
  },

  async createQuestion(
    data: Question
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request('/qs/questions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateQuestion(
    questionId: number,
    data: Partial<Question>
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request(`/qs/questions/${questionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteQuestion(
    questionId: number
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request(`/qs/questions/${questionId}`, {
      method: 'DELETE',
    });
  },

  // ------------------ CATEGORY ------------------

  async getAllCategories(): Promise<ApiResponse<{ categories: string[] }>> {
    return apiClient.request('/qs/category/', {
      method: 'GET',
    });
  },

  async createCategory(
    data: Category
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request('/qs/category/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateCategory(data: {
    name: string;
    new_name: string;
  }): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request(`/qs/category/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteCategory(
    data: Category
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request(`/qs/category/`, {
      method: 'DELETE',
      body: JSON.stringify(data),
    });
  },

  // ------------------ DIFFICULTY ------------------

  async getAllDifficulties(): Promise<ApiResponse<{ difficulties: string[] }>> {
    return apiClient.request('/qs/difficulty/', {
      method: 'GET',
    });
  },

  async createDifficulty(
    data: Difficulty
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request('/qs/difficulty/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateDifficulty(data: {
    level: string;
    new_level: string;
  }): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request(`/qs/difficulty/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteDifficulty(
    data: Difficulty
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.request(`/qs/difficulty/`, {
      method: 'DELETE',
      body: JSON.stringify(data),
    });
  },

  // ------------------ POOL ------------------
  async getPoolCategories(): Promise<ApiResponse<{ categories: string[] }>> {
    return apiClient.request('/qs/pool/category/', {
      method: 'GET',
    });
  },

  async getPoolDifficultiesByCategory(
    category: string
  ): Promise<ApiResponse<{ difficulty_levels: string[] }>> {
    return apiClient.request(
      `/qs/pool/${encodeURIComponent(category)}/difficulty/`,
      {
        method: 'GET',
      }
    );
  },

  async getRandomQuestionFromPool(
    category: string,
    difficulty: string
  ): Promise<ApiResponse<PoolQuestion>> {
    return apiClient.request(
      `/qs/pool/${encodeURIComponent(category)}/${encodeURIComponent(difficulty)}/`,
      {
        method: 'GET',
      }
    );
  },
};
