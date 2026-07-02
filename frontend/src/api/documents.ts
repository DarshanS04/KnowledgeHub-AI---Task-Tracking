import { apiClient } from './client';
import { DocumentResponse } from '../types';

export const documentsApi = {
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<{ data: DocumentResponse }>(
      '/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.data;
  },

  createNote: async (title: string, content: string) => {
    const response = await apiClient.post<{ data: DocumentResponse }>('/documents/notes', {
      title,
      content,
    });
    return response.data.data;
  },

  listDocuments: async (page = 1, size = 10) => {
    const response = await apiClient.get(`/documents?page=${page}&size=${size}`);
    return response.data; // returns PaginatedResponse structure
  },

  deleteDocument: async (id: string) => {
    const response = await apiClient.delete<{ data: string }>(`/documents/${id}`);
    return response.data.data;
  },

  cloneGithub: async (repoUrl: string) => {
    const response = await apiClient.post<{ data: DocumentResponse }>('/github', {
      repo_url: repoUrl,
    });
    return response.data.data;
  },

  importYoutube: async (videoUrl: string) => {
    const response = await apiClient.post<{ data: DocumentResponse }>('/youtube', {
      video_url: videoUrl,
    });
    return response.data.data;
  },
};
