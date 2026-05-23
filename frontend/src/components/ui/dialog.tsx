import type { ReactNode } from "react";

export function Dialog({ children }: { children: ReactNode }) {
  return <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/60 p-6">{children}</div>;
}
