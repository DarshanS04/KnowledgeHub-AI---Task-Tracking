import { apiClient } from './client';
import { ConversationResponse, MessageResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const chatApi = {
  listConversations: async (page = 1, size = 20) => {
    const response = await apiClient.get(`/chat/history?page=${page}&size=${size}`);
    return response.data; // returns PaginatedResponse structure
  },

  getMessages: async (conversationId: string) => {
    const response = await apiClient.get<{ data: MessageResponse[] }>(`/chat/history/${conversationId}`);
    return response.data.data;
  },

  deleteConversation: async (conversationId: string) => {
    const response = await apiClient.delete<{ data: string }>(`/chat/${conversationId}`);
    return response.data.data;
  },

  renameConversation: async (conversationId: string, title: string) => {
    const response = await apiClient.put<{ data: ConversationResponse }>(`/chat/${conversationId}`, {
      title,
    });
    return response.data.data;
  },

  /**
   * Triggers SSE streaming chat query.
   * Calls custom fetch to read readable body stream token chunks and citations.
   */
  streamChat: async function* (
    message: string,
    conversationId?: string
  ): AsyncGenerator<{ event: string; data: any }, void, unknown> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId || null,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Readable stream not supported.');
    }

    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Split by double newline to parse SSE data format
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || ''; // Keep trailing partial chunk in buffer

        for (const part of parts) {
          const line = part.trim();
          if (line.startsWith('data: ')) {
            try {
              const parsed = JSON.parse(line.slice(6));
              yield { event: parsed.event, data: parsed.data || parsed };
            } catch (e) {
              console.error('Failed to parse SSE line data:', line, e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};
