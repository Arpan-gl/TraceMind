import json
from collections.abc import Mapping

import aio_pika

from app.core.rabbitmq import rabbitmq_url, inference_queue_name


async def publish_telemetry(payload: Mapping[str, object]) -> None:
    connection = await aio_pika.connect_robust(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(inference_queue_name, durable=True)
        message = aio_pika.Message(body=json.dumps(dict(payload), default=str).encode("utf-8"), delivery_mode=aio_pika.DeliveryMode.PERSISTENT)
        await channel.default_exchange.publish(message, routing_key=inference_queue_name)
