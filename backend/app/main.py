from fastapi import FastAPI

from app.api import auth, chat, conversations, ingestion, metrics

app = FastAPI(title="TraceMind API", version="0.1.0")

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(ingestion.router)
app.include_router(metrics.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
