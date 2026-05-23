import React from "react";
import { AuthPage } from "../components/AuthPage";

export function Intro() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900/60 via-transparent to-slate-900/10 text-white">
      <div className="mx-auto flex max-w-6xl items-stretch gap-10 px-6 py-12">
        <div className="hidden w-1/2 flex-col gap-6 rounded-3xl bg-gradient-to-b from-slate-950/80 to-slate-900/70 p-8 text-white lg:flex">
          <h1 className="text-4xl font-bold">TraceMind</h1>
          <p className="text-lg text-slate-300">Stream and analyze LLM inference logs, manage conversations, and inspect telemetry in real-time.</p>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            <li>• Streaming responses over POST + fetch</li>
            <li>• Ingestion worker with resilient retries</li>
            <li>• Observability: Prometheus & Grafana</li>
          </ul>
          <div className="mt-auto flex items-center gap-3">
            <button className="rounded-full bg-sky-600 px-4 py-2 text-sm font-semibold">Learn more</button>
            <button className="rounded-full border border-white/10 px-4 py-2 text-sm">Docs</button>
          </div>
        </div>

        <div className="w-full lg:w-1/2">
          <AuthPage />
        </div>
      </div>
    </div>
  );
}

export default Intro;
