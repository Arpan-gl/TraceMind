from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "route"],
)

inference_requests_total = Counter(
    "inference_requests_total",
    "Total inference requests",
    ["provider", "model", "status"],
)

inference_latency_seconds = Histogram(
    "inference_latency_seconds",
    "Inference latency in seconds",
    ["provider", "model"],
)

inference_tokens_total = Counter(
    "inference_tokens_total",
    "Inference tokens total",
    ["type", "provider"],
)

ingestion_events_total = Counter(
    "ingestion_events_total",
    "Total telemetry ingestion events handled by the worker",
    ["status"],
)

ingestion_duration_seconds = Histogram(
    "ingestion_duration_seconds",
    "Telemetry ingestion persistence latency in seconds",
    ["status"],
)
