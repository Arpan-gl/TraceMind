import { useState, type FormEvent } from "react";

import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useAppContext } from "../state/app-context";

export function AuthPage() {
  const { authMode, setAuthMode, signIn, registerAccount, setError, error } = useAppContext();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (authMode === "login") {
        await signIn(email, password);
      } else {
        await registerAccount(email, password);
      }
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-6 text-white">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-3xl border border-white/10 bg-slate-950/90 p-8 shadow-2xl backdrop-blur">
        <p className="text-sm uppercase tracking-[0.35em] text-sky-300">TraceMind</p>
        <h1 className="mt-3 text-3xl font-semibold">{authMode === "login" ? "Sign in" : "Create account"}</h1>
        <p className="mt-2 text-sm text-slate-300">Log in to continue the chat and telemetry workflow.</p>
        <div className="mt-6 space-y-4">
          <Input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" type="email" />
          <Input value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" type="password" />
        </div>
        {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
        <div className="mt-6 flex items-center gap-3">
          <Button type="submit" disabled={submitting} className="bg-sky-500 hover:bg-sky-400">{authMode === "login" ? "Sign in" : "Register"}</Button>
          <button
            className="text-sm text-slate-300 underline underline-offset-4"
            type="button"
            onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}
          >
            {authMode === "login" ? "Need an account?" : "Have an account?"}
          </button>
        </div>
      </form>
    </main>
  );
}
