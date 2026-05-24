from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import uuid4

from app.core.observability import inference_latency_seconds, inference_requests_total, inference_tokens_total
from app.sdk.pii_redactor import redact
from app.sdk.telemetry import publish_telemetry


class LLMWrapper:
    def __init__(self, provider: str, model: str, api_key: str):
        self.provider = provider
        self.model = model
        self.api_key = api_key

    async def generate_stream(
        self,
        messages: list,
        session_id: str,
        conversation_id: str,
        max_output_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        start_time = time.perf_counter()
        request_preview = redact((messages[-1].get("content", "") if messages else "")[:200])
        response_parts: list[str] = []
        status = "success"
        error_message: str | None = None
        tokens_input = sum(max(1, len(message.get("content", "")) // 4) for message in messages)
        tokens_output = 0

        try:
            if self.provider == "groq" and self.api_key:
                from groq import AsyncGroq

                client = AsyncGroq(api_key=self.api_key)
                stream = await client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    max_tokens=max_output_tokens,
                )
                async for event in stream:
                    chunk = event.choices[0].delta.content or ""
                    if not chunk:
                        continue
                    response_parts.append(chunk)
                    tokens_output += max(1, len(chunk) // 4)
                    yield chunk
            else:
                fallback_text = " ".join(message.get("content", "") for message in messages if message.get("content"))
                if max_output_tokens is not None:
                    fallback_text = fallback_text[: max_output_tokens * 4]
                for index in range(0, len(fallback_text), 32):
                    chunk = fallback_text[index : index + 32]
                    response_parts.append(chunk)
                    tokens_output += max(1, len(chunk) // 4)
                    yield chunk
                    await asyncio.sleep(0)
        except Exception as exc:  # pragma: no cover - stream error path
            status = "error"
            error_message = str(exc)
            raise
        finally:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            telemetry = {
                "id": str(uuid4()),
                "provider": self.provider,
                "model": self.model,
                "latency_ms": latency_ms,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "status": status,
                "error_message": error_message,
                "request_preview": request_preview,
                "response_preview": redact("".join(response_parts)[:200]),
                "session_id": session_id,
                "conversation_id": conversation_id,
                "created_at": datetime.now(timezone.utc),
            }
            inference_requests_total.labels(self.provider, self.model, status).inc()
            inference_latency_seconds.labels(self.provider, self.model).observe(latency_ms / 1000.0)
            inference_tokens_total.labels("input", self.provider).inc(tokens_input)
            inference_tokens_total.labels("output", self.provider).inc(tokens_output)
            try:
                await publish_telemetry(telemetry)
            except Exception:
                pass
