from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import db_session, require_internal_secret
from app.models.inference_log import InferenceLog
from app.schemas import InferenceLogPayload

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/log", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_internal_secret)])
async def ingest_log(payload: InferenceLogPayload, session: AsyncSession = Depends(db_session)) -> dict[str, str]:
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
    return {"detail": "stored"}
