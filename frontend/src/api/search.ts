import { apiClient } from './client';
import { SearchResult } from '../types';

export const searchApi = {
  executeSearch: async (query: string, sourceType?: string, limit = 5) => {
    const response = await apiClient.post<{ data: SearchResult[] }>('/search', {
      query,
      source_type: sourceType || null,
      limit,
    });
    return response.data.data;
  },
};
