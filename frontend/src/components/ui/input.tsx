import type { InputHTMLAttributes } from "react";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={["w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-white placeholder:text-slate-400", props.className].filter(Boolean).join(" ")} />;
}
