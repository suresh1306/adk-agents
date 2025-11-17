/**
 * Type definitions for Tour Planner Chat UI
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  status: 'executing' | 'completed' | 'failed';
  timestamp: Date;
}

export interface Session {
  session_id: string;
  user_id: string;
  app_name: string;
  state: Record<string, any>;
  last_update_time: number;
  event_count: number;
  created_at?: Date;
  title?: string;
}

export interface ChatRequest {
  message: string;
  user_id: string;
  session_id?: string;
  stream?: boolean;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  user_id: string;
}

export interface StreamEvent {
  type: 'content' | 'tool_call' | 'tool_result' | 'done' | 'error';
  text?: string;
  role?: string;
  tool?: string;
  status?: string;
  message?: string;
  error_type?: string;
  session_id?: string;
}

export interface SessionCreate {
  user_id: string;
  session_id?: string;
  initial_state?: Record<string, any>;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  app_name: string;
  session_service: string;
}

export type ChatState = 'idle' | 'loading' | 'streaming' | 'error';
