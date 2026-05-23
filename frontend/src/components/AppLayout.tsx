import { Button } from "./ui/button";
import { ConversationSidebar } from "./ConversationSidebar";
import { ChatWindow } from "./ChatWindow";
import { useAppContext } from "../state/app-context";

export function AppLayout() {
  const { signOut } = useAppContext();

  return (
    <main className="flex min-h-screen flex-col overflow-hidden bg-slate-900 lg:flex-row">
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950 px-4 py-3 text-white lg:hidden">
        <span className="text-sm uppercase tracking-[0.35em] text-sky-300">TraceMind</span>
        <Button type="button" className="bg-white/10 hover:bg-white/15" onClick={signOut}>
          Sign out
        </Button>
      </div>
      <ConversationSidebar />
      <ChatWindow />
    </main>
  );
}
