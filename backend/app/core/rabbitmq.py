from app.core.config import get_settings

settings = get_settings()
rabbitmq_url = settings.rabbitmq_url
inference_queue_name = "inference_logs"
dlq_queue_name = "inference_logs.dlq"
