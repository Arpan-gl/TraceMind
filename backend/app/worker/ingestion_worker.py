from __future__ import annotations

import asyncio
import json
import logging

import aio_pika
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.db import async_session_factory
from app.core.observability import inference_latency_seconds, inference_requests_total, inference_tokens_total
from app.models.inference_log import InferenceLog
from app.schemas import InferenceLogPayload

logger = logging.getLogger(__name__)


async def _persist_payload(payload: InferenceLogPayload) -> None:
    async with async_session_factory() as session:
        log_entry = InferenceLog(
            id=payload.id,
            conversation_id=payload.conversation_id,
            provider=payload.provider,
            model=payload.model,
            latency_ms=payload.latency_ms,
            tokens_input=payload.tokens_input,
            tokens_output=payload.tokens_output,
            status=payload.status,
            error_message=payload.error_message,
            request_preview=payload.request_preview,
            response_preview=payload.response_preview,
            session_id=payload.session_id,
        )
        session.add(log_entry)
        await session.commit()


async def _handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process(ignore_processed=True, requeue=False):
        try:
            payload = InferenceLogPayload.model_validate_json(message.body)
        except ValidationError as exc:
            logger.exception("invalid telemetry payload: %s", exc)
            return

        try:
            await _persist_payload(payload)
        except Exception:
            logger.exception("failed to persist telemetry payload")
            raise

        inference_requests_total.labels(payload.provider, payload.model, payload.status).inc()
        inference_latency_seconds.labels(payload.provider, payload.model).observe(payload.latency_ms / 1000.0)
        inference_tokens_total.labels("input", payload.provider).inc(payload.tokens_input)
        inference_tokens_total.labels("output", payload.provider).inc(payload.tokens_output)


async def main() -> None:
    settings = get_settings()
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("inference_logs", durable=True)
        await queue.consume(_handle_message)
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
