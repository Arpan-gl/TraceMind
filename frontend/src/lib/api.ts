import axios from "axios";
import { clearToken, getToken } from "./auth";
import type { AuthResponse, Conversation, Message } from "./types";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function register(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/register", { email, password });
  return data;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/login", { email, password });
  return data;
}

export async function listConversations(): Promise<Conversation[]> {
  const { data } = await api.get<Conversation[]>("/conversations");
  return data;
}

export async function createConversation(title: string): Promise<Conversation> {
  const { data } = await api.post<Conversation>("/conversations", { title });
  return data;
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await api.delete(`/conversations/${conversationId}`);
}

export async function getConversationMessages(conversationId: string): Promise<Message[]> {
  const { data } = await api.get<Message[]>(`/conversations/${conversationId}/messages`);
  return data;
}

export function signOut(): void {
  clearToken();
}
