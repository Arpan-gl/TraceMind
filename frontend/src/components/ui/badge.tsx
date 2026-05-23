import type { HTMLAttributes } from "react";

export function Badge(props: HTMLAttributes<HTMLSpanElement>) {
  return <span {...props} className={["inline-flex rounded-full bg-white/10 px-2 py-0.5 text-xs text-slate-200", props.className].filter(Boolean).join(" ")} />;
}
