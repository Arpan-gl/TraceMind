import { useState } from "react";

import { Trash2 } from "lucide-react";

import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Dialog } from "./ui/dialog";
import { ScrollArea } from "./ui/scroll-area";
import { Skeleton } from "./ui/skeleton";
import { Tooltip } from "./ui/tooltip";
import { formatRelativeTime } from "../lib/time";
import { useAppContext } from "../state/app-context";

export function ConversationSidebar() {
  const {
    conversations,
    activeConversationId,
    loadingConversations,
    error,
    startConversation,
    openConversation,
    removeConversation,
    signOut,
  } = useAppContext();
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  const pendingConversation = conversations.find((conversation) => conversation.id === pendingDeleteId) ?? null;

  async function confirmDelete(): Promise<void> {
    if (!pendingDeleteId) {
      return;
    }
    await removeConversation(pendingDeleteId);
    setPendingDeleteId(null);
  }

  return (
    <aside className="flex w-full shrink-0 flex-col border-r border-slate-800 bg-slate-950 text-slate-100 lg:w-72">
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-sky-300">TraceMind</p>
            <div className="text-xs text-slate-400">AI Assistant</div>
          </div>
          <Button type="button" className="bg-white/6 hover:bg-white/8" onClick={signOut}>
            Sign out
          </Button>
        </div>
        <div className="mt-4">
          <Button type="button" onClick={() => void startConversation()} disabled={loadingConversations} className="w-full bg-sky-600 hover:bg-sky-500">
          New Chat
        </Button>
        </div>
        {error ? <p className="mt-3 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-200">{error}</p> : null}
      </div>
      <div className="flex-1 overflow-hidden px-3 pb-3">
        <ScrollArea className="h-full pr-1">
          {loadingConversations ? (
            <div className="space-y-3 p-2">
              <Skeleton className="h-14 w-full bg-white/10" />
              <Skeleton className="h-14 w-full bg-white/10" />
              <Skeleton className="h-14 w-full bg-white/10" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">No conversations yet.</div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <div key={conversation.id} className={[
                  "rounded-2xl px-3 py-3 transition",
                  activeConversationId === conversation.id ? "bg-white/12" : "hover:bg-white/6",
                ].join(" ")}>
                  <div className="flex items-start justify-between gap-2">
                    <button type="button" onClick={() => void openConversation(conversation.id)} className="min-w-0 flex-1 text-left">
                      <div className="truncate text-sm font-medium">{conversation.title}</div>
                      <div className="mt-1 text-xs text-slate-400">{formatRelativeTime(conversation.updated_at)}</div>
                    </button>
                    <Tooltip>
                      <Button
                        type="button"
                        className="h-8 rounded-full bg-white/10 px-3 text-xs hover:bg-white/15"
                        onClick={() => setPendingDeleteId(conversation.id)}
                        aria-label={`Delete ${conversation.title}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </Tooltip>
                  </div>
                  {activeConversationId === conversation.id ? <Badge className="mt-2 bg-sky-500/20 text-sky-200">Active</Badge> : null}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>
      {pendingConversation ? (
        <Dialog>
          <div className="w-full max-w-sm rounded-3xl border border-slate-200 bg-white p-6 text-slate-900 shadow-2xl">
            <h3 className="text-lg font-semibold">Delete conversation?</h3>
            <p className="mt-2 text-sm text-slate-500">This will archive {pendingConversation.title} and remove it from the sidebar.</p>
            <div className="mt-6 flex items-center justify-end gap-3">
              <Button type="button" className="bg-slate-100 text-slate-900 hover:bg-slate-200" onClick={() => setPendingDeleteId(null)}>
                Cancel
              </Button>
              <Button type="button" className="bg-red-600 hover:bg-red-500" onClick={() => void confirmDelete()}>
                Delete
              </Button>
            </div>
          </div>
        </Dialog>
      ) : null}
    </aside>
  );
}
