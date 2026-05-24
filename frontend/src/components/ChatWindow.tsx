import { useEffect, useMemo, useState, type FormEvent } from "react";

import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import { Separator } from "./ui/separator";
import { Skeleton } from "./ui/skeleton";
import { Textarea } from "./ui/textarea";
import { streamChatResponse } from "../lib/stream";
import type { Message } from "../lib/types";
import { useAppContext } from "../state/app-context";

export function ChatWindow() {
  const { activeConversationId, messages, loadingMessages, startConversation } = useAppContext();
  const [draft, setDraft] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamText, setStreamText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [controller, setController] = useState<AbortController | null>(null);
  const [displayMessages, setDisplayMessages] = useState<Message[]>(messages);

  useEffect(() => {
    setDisplayMessages(messages);
  }, [messages]);

  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim() || isStreaming) {
      return;
    }

    let conversationId = activeConversationId;
    if (!conversationId) {
      try {
        const conversation = await startConversation();
        conversationId = conversation.id;
      } catch (conversationError) {
        setError(conversationError instanceof Error ? conversationError.message : "Could not start a new chat");
        return;
      }
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      conversation_id: conversationId,
      role: "user",
      content: draft,
      token_count: Math.max(1, Math.ceil(draft.length / 4)),
      created_at: new Date().toISOString(),
    };

    setDisplayMessages((current) => [...current, userMessage]);
    setDraft("");
    setError(null);
    setIsStreaming(true);
    setStreamText("");

    const abortController = new AbortController();
    setController(abortController);
    let assistantText = "";

    try {
      await streamChatResponse(
        `${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"}/chat/${conversationId}/stream`,
        {
          message: userMessage.content,
          provider: "groq",
          model: "llama-3.1-8b-instant",
          session_id: crypto.randomUUID(),
        },
        (chunk) => {
          assistantText += chunk;
          setStreamText((current) => current + chunk);
        },
        abortController.signal,
      );
      setDisplayMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          conversation_id: conversationId,
          role: "assistant",
          content: assistantText,
          token_count: Math.max(1, Math.ceil(assistantText.length / 4)),
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (sendError) {
      if (!(sendError instanceof DOMException && sendError.name === "AbortError")) {
        setError(sendError instanceof Error ? sendError.message : "Chat stream failed");
      }
    } finally {
      setIsStreaming(false);
      setController(null);
    }
  }

  function stopStream() {
    controller?.abort();
    setController(null);
    setIsStreaming(false);
  }

  const visibleMessages = useMemo(
    () => (isStreaming && streamText ? [...displayMessages, { id: "streaming", conversation_id: activeConversationId ?? "", role: "assistant", content: streamText, token_count: 0, created_at: new Date().toISOString() }] : displayMessages),
    [activeConversationId, displayMessages, isStreaming, streamText],
  );

  return (
    <section className="flex h-full flex-1 flex-col bg-slate-900 text-slate-100">
      <div className="border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Chat</h2>
            <p className="text-sm text-slate-500">Streaming responses over POST + fetch</p>
          </div>
          <div className="flex items-center gap-2">
            {isStreaming ? <Badge className="bg-emerald-500/20 text-emerald-700">Streaming</Badge> : null}
            {isStreaming ? <Button type="button" onClick={stopStream}>Stop</Button> : null}
          </div>
        </div>
      </div>
      <ScrollArea className="flex-1 px-6 py-6">
        {loadingMessages ? (
          <div className="space-y-4">
            <Skeleton className="h-20 w-2/3" />
            <Skeleton className="h-20 w-1/2" />
            <Skeleton className="h-20 w-3/4" />
          </div>
        ) : (
          <div className="space-y-4">
            {visibleMessages.map((message) => (
                <div
                  key={message.id}
                  className={message.role === "user" ? "ml-auto max-w-2xl rounded-3xl bg-sky-600 px-4 py-3 text-white" : "max-w-2xl rounded-3xl bg-slate-800 px-4 py-3 shadow-sm ring-1 ring-slate-700 text-slate-100"}
                >
                  <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
                </div>
              ))}
            {isStreaming ? (
              <div className="max-w-2xl rounded-3xl bg-white px-4 py-3 shadow-sm ring-1 ring-slate-200">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-sky-500" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-sky-500 [animation-delay:150ms]" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-sky-500 [animation-delay:300ms]" />
                  <span>Typing...</span>
                </div>
              </div>
            ) : null}
          </div>
        )}
      </ScrollArea>
      <Separator />
      <form onSubmit={handleSend} className="border-t border-slate-800 bg-slate-900 p-4">
        <div className="flex items-end gap-3">
          <Textarea value={draft} onChange={(event) => setDraft(event.target.value)} rows={3} placeholder="Send a message" />
          <Button type="submit" disabled={!draft.trim() || isStreaming}>
            Send
          </Button>
        </div>
        {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
      </form>
    </section>
  );
}
