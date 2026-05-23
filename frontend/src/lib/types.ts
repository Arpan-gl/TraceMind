export interface Conversation {
  id: string;
  title: string;
  updated_at?: string | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  token_count: number;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
