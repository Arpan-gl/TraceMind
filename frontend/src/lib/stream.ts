import { getToken } from "./auth";

export async function streamChatResponse(
  url: string,
  body: unknown,
  onChunk: (chunk: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok || !response.body) {
    const detail = await response.text();
    let message = detail || "stream request failed";
    try {
      const parsed = JSON.parse(detail) as { detail?: string };
      message = parsed.detail || message;
    } catch {
      message = detail || message;
    }
    throw new Error(message);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const eventType = part
        .split("\n")
        .find((line) => line.startsWith("event: "))
        ?.slice(7);
      const dataLines = part
        .split("\n")
        .filter((line) => line.startsWith("data: "))
        .map((line) => line.slice(6));
      if (dataLines.length > 0) {
        const payload = dataLines.join("\n");
        if (eventType === "error") {
          throw new Error(payload || "stream request failed");
        }
        onChunk(payload);
      }
    }
  }
}
