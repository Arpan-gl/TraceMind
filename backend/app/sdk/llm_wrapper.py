from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from uuid import uuid4

from app.sdk.pii_redactor import redact
from app.sdk.telemetry import publish_telemetry


class LLMWrapper:
    def __init__(self, provider: str, model: str, api_key: str):
        self.provider = provider
        self.model = model
        self.api_key = api_key

    async def generate_stream(self, messages: list, session_id: str, conversation_id: str) -> AsyncGenerator[str, None]:
        start_time = time.perf_counter()
        request_preview = redact((messages[-1].get("content", "") if messages else "")[:200])
        response_parts: list[str] = []
        status = "success"
        error_message: str | None = None
        tokens_input = sum(max(1, len(message.get("content", "")) // 4) for message in messages)
        tokens_output = 0

        try:
            for message in messages:
                content = message.get("content", "")
                if not content:
                    continue
                chunk = content[:32]
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
            telemetry = {
                "id": str(uuid4()),
                "provider": self.provider,
                "model": self.model,
                "latency_ms": (end_time - start_time) * 1000,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "status": status,
                "error_message": error_message,
                "request_preview": request_preview,
                "response_preview": redact("".join(response_parts)[:200]),
                "session_id": session_id,
                "conversation_id": conversation_id,
                "created_at": time.time(),
            }
            try:
                asyncio.create_task(publish_telemetry(telemetry))
            except RuntimeError:
                pass
