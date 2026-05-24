from __future__ import annotations

import asyncio
import logging
import random
import time

import aio_pika
from pydantic import ValidationError
from prometheus_client import start_http_server

from app.core.config import get_settings
from app.core.db import async_session_factory
from app.core.observability import ingestion_duration_seconds, ingestion_events_total
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
    start_time = time.perf_counter()
    message_status = "success"
    async with message.process(ignore_processed=True, requeue=False):
        try:
            payload = InferenceLogPayload.model_validate_json(message.body)
        except ValidationError as exc:
            message_status = "invalid"
            logger.exception("invalid telemetry payload: %s", exc)
            ingestion_events_total.labels(message_status).inc()
            ingestion_duration_seconds.labels(message_status).observe(time.perf_counter() - start_time)
            return

        try:
            await _persist_payload(payload)
        except Exception:
            message_status = "error"
            logger.exception("failed to persist telemetry payload")
            ingestion_events_total.labels(message_status).inc()
            ingestion_duration_seconds.labels(message_status).observe(time.perf_counter() - start_time)
            raise

        ingestion_events_total.labels(message_status).inc()
        ingestion_duration_seconds.labels(message_status).observe(time.perf_counter() - start_time)


async def main() -> None:
    settings = get_settings()
    start_http_server(settings.worker_metrics_port)
    logger.info("worker metrics listening on :%s", settings.worker_metrics_port)
    # Resilient connection loop with exponential backoff and jitter.
    backoff = 1.0
    max_backoff = 60.0
    while True:
        try:
            logger.info("connecting to RabbitMQ at %s", settings.rabbitmq_url)
            connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("inference_logs", durable=True)
                await queue.consume(_handle_message)
                logger.info("connected to RabbitMQ and consuming from inference_logs")
                # Reset backoff after successful connect
                backoff = 1.0
                # Wait forever until the connection is lost or cancelled
                await asyncio.Event().wait()
        except asyncio.CancelledError:
            # allow clean shutdown
            raise
        except Exception:
            logger.exception("failed to connect/consume from RabbitMQ, retrying in %.1fs", backoff)
            # sleep with jitter
            jitter = random.random() * 0.5 * backoff
            await asyncio.sleep(backoff + jitter)
            backoff = min(backoff * 2, max_backoff)


if __name__ == "__main__":
    asyncio.run(main())
