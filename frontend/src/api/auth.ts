import { apiClient } from './client';
import { SignupRequest, LoginRequest, TokenResponse, UserResponse } from '../types';

export const authApi = {
  signup: async (data: SignupRequest) => {
    const response = await apiClient.post<{ data: UserResponse }>('/auth/signup', data);
    return response.data.data;
  },

  login: async (data: LoginRequest) => {
    const response = await apiClient.post<{ data: TokenResponse }>('/auth/login', data);
    return response.data.data;
  },

  logout: async (refreshToken: string) => {
    const response = await apiClient.post<{ data: string }>('/auth/logout', { refresh_token: refreshToken });
    return response.data.data;
  },
};
