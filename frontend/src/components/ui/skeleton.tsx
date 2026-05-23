import React from "react";

export function Skeleton(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className = "", ...rest } = props;
  return (
    <div
      className={["animate-pulse rounded-md bg-white/10", className].filter(Boolean).join(" ")}
      {...rest}
    />
  );
}
