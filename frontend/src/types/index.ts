// ==============================================================================
// KnowledgeHub AI - Frontend TypeScript Definitions
// ==============================================================================

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SignupRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserResponse;
}

export interface DocumentResponse {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  source_type: 'pdf' | 'docx' | 'txt' | 'md' | 'github' | 'youtube' | 'notes';
  source_url?: string;
  file_size?: number;
  total_chunks: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  meta_info: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{
    filename: string;
    page_number?: number;
    chunk_number: number;
    snippet: string;
    similarity_score: number;
  }>;
  token_count?: number;
  response_time?: number;
  created_at: string;
}

export interface ConversationResponse {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface SystemStatsResponse {
  total_users: number;
  total_documents: number;
  total_chunks: number;
  total_conversations: number;
  total_messages: number;
}

export interface SearchResult {
  filename: string;
  page?: number;
  chunk_number: number;
  similarity_score: number;
  preview_snippet: string;
  document_id: string;
}

