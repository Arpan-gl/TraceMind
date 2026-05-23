from prometheus_client import Counter, Histogram

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
