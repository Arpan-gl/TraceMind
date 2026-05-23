import type { HTMLAttributes } from "react";

export function ScrollArea(props: HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={["overflow-auto", props.className].filter(Boolean).join(" ")} />;
}
