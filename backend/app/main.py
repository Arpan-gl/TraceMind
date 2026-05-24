import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, conversations, ingestion, metrics
from app.core.config import get_settings
from app.core.observability import http_request_duration_seconds, http_requests_total

app = FastAPI(title="TraceMind API", version="0.1.0")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def record_http_metrics(request, call_next):
    start_time = time.perf_counter()
    status_code = 500
    route = request.url.path
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        route_template = request.scope.get("route")
        if route_template is not None and getattr(route_template, "path", None):
            route = route_template.path
        elapsed = time.perf_counter() - start_time
        http_requests_total.labels(request.method, route, str(status_code)).inc()
        http_request_duration_seconds.labels(request.method, route).observe(elapsed)


app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(ingestion.router)
app.include_router(metrics.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
