import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import {
  createConversation,
  deleteConversation,
  getConversationMessages,
  listConversations,
  login,
  register,
  signOut as clearSession,
} from "../lib/api";
import { clearToken, getToken, setToken } from "../lib/auth";
import type { AuthResponse, Conversation, Message } from "../lib/types";

interface AppContextValue {
  token: string | null;
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Message[];
  loadingConversations: boolean;
  loadingMessages: boolean;
  authMode: "login" | "register";
  error: string | null;
  setAuthMode: (mode: "login" | "register") => void;
  signIn: (email: string, password: string) => Promise<void>;
  registerAccount: (email: string, password: string) => Promise<void>;
  signOut: () => void;
  refreshConversations: () => Promise<void>;
  openConversation: (conversationId: string) => Promise<void>;
  startConversation: () => Promise<void>;
  removeConversation: (conversationId: string) => Promise<void>;
  setError: (error: string | null) => void;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

async function persistAuth(result: AuthResponse): Promise<void> {
  setToken(result.access_token);
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(getToken());
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setTokenState(getToken());
  }, []);

  async function signIn(email: string, password: string): Promise<void> {
    const result = await login(email, password);
    await persistAuth(result);
    setTokenState(result.access_token);
  }

  async function registerAccount(email: string, password: string): Promise<void> {
    const result = await register(email, password);
    await persistAuth(result);
    setTokenState(result.access_token);
  }

  function signOut(): void {
    clearSession();
    clearToken();
    setTokenState(null);
    setConversations([]);
    setActiveConversationId(null);
    setMessages([]);
  }

  async function refreshConversations(): Promise<void> {
    setLoadingConversations(true);
    try {
      const items = await listConversations();
      setConversations(items);
      if (!activeConversationId && items.length > 0) {
        setActiveConversationId(items[0].id);
      }
    } finally {
      setLoadingConversations(false);
    }
  }

  async function openConversation(conversationId: string): Promise<void> {
    setActiveConversationId(conversationId);
    setLoadingMessages(true);
    try {
      const history = await getConversationMessages(conversationId);
      setMessages(history);
    } finally {
      setLoadingMessages(false);
    }
  }

  async function startConversation(): Promise<void> {
    const conversation = await createConversation("New conversation");
    setConversations((current) => [conversation, ...current]);
    await openConversation(conversation.id);
  }

  async function removeConversation(conversationId: string): Promise<void> {
    await deleteConversation(conversationId);
    setConversations((current) => current.filter((conversation) => conversation.id !== conversationId));
    if (activeConversationId === conversationId) {
      setActiveConversationId(null);
      setMessages([]);
    }
  }

  useEffect(() => {
    if (token) {
      void refreshConversations();
    }
  }, [token]);

  const value = useMemo<AppContextValue>(
    () => ({
      token,
      conversations,
      activeConversationId,
      messages,
      loadingConversations,
      loadingMessages,
      authMode,
      error,
      setAuthMode,
      signIn,
      registerAccount,
      signOut,
      refreshConversations,
      openConversation,
      startConversation,
      removeConversation,
      setError,
    }),
    [
      activeConversationId,
      authMode,
      conversations,
      error,
      loadingConversations,
      loadingMessages,
      messages,
      token,
    ],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used within AppProvider");
  }
  return context;
}
