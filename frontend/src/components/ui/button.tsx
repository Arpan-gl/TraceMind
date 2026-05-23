import type { ButtonHTMLAttributes } from "react";

export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={["rounded-md bg-sky-500 px-4 py-2 font-medium text-white", props.className].filter(Boolean).join(" ")} />;
}
