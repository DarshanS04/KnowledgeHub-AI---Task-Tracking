import { apiClient } from './client';
import { SystemStatsResponse, UserResponse } from '../types';

export const adminApi = {
  getStats: async () => {
    const response = await apiClient.get<{ data: SystemStatsResponse }>('/admin/stats');
    return response.data.data;
  },

  listUsers: async (page = 1, size = 100) => {
    const response = await apiClient.get<{ data: UserResponse[] }>(`/admin/users?page=${page}&size=${size}`);
    return response.data.data;
  },

  deleteUser: async (id: string) => {
    const response = await apiClient.delete<{ data: string }>(`/admin/users/${id}`);
    return response.data.data;
  },

  listUploadLogs: async (page = 1, size = 100) => {
    const response = await apiClient.get<{ data: any[] }>(`/admin/upload-logs?page=${page}&size=${size}`);
    return response.data.data;
  },

  listProcessingQueue: async (page = 1, size = 100) => {
    const response = await apiClient.get<{ data: any[] }>(`/admin/processing-queue?page=${page}&size=${size}`);
    return response.data.data;
  },
};
