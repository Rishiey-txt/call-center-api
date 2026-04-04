import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.request import CallAnalyticsRequest
from src.models.response import CallAnalyticsResponse
from src.dependencies import verify_api_key, get_db
from src.tasks.processing import process_call
from src.db.models import CallLog

router = APIRouter()

@router.post("/api/call-analytics", response_model=CallAnalyticsResponse)
async def call_analytics(
    body: CallAnalyticsRequest,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
) -> CallAnalyticsResponse:
    call_id = str(uuid.uuid4())

    # Dispatch Celery task (runs synchronously in EAGER mode)
    result = process_call.delay(
        audio_base64=body.audioBase64,
        language=body.language,
        call_id=call_id,
    ).get(timeout=120)   # 2 min max for long audio

        # Persist all dynamic fields securely into Database
    log = CallLog(
        id=call_id,
        language=body.language,
        transcript=result.get("transcript", ""),
        summary=result.get("summary", ""),
        payment=result.get("analytics", {}).get("paymentPreference", ""),
        rejection=result.get("analytics", {}).get("rejectionReason", ""),
        sentiment=result.get("analytics", {}).get("sentiment", ""),
        compliance=result.get("sop_validation", {}).get("complianceScore", 0.0),
        adherence=result.get("sop_validation", {}).get("adherenceStatus", ""),
        raw_response=result,
    )
    db.add(log)
    await db.commit()


    return CallAnalyticsResponse(**result)
