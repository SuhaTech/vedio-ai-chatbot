import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.schemas import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    # Dev-mode: stream a short mocked answer for frontend testing without heavy deps
    if settings.dev_mode:
        async def dev_stream():
            # stream a few tokens
            tokens = [
                "Sure — here's a quick analysis:\n",
                "Video A has higher likes and a stronger hook in the first 5s.\n",
                "Engagement A: 15.6% vs B: 8.5%.\n",
                "Suggestion: Make the first 3s clearer and include caption CTA.\n",
            ]
            for t in tokens:
                yield f"data: {json.dumps({'type':'token','token': t})}\n\n"
            citations = [
                {"video_id": "A", "platform": "youtube", "chunk_index": 0, "source_url": ""},
                {"video_id": "B", "platform": "instagram", "chunk_index": 0, "source_url": ""},
            ]
            yield f"data: {json.dumps({'type':'done','citations': citations})}\n\n"

        return StreamingResponse(dev_stream(), media_type="text/event-stream")

    # Production path: lazy import of retrieval_service to avoid hard failures at import time
    try:
        from app.services.retrieval_service import retrieval_service
    except Exception as exc:
        async def err_stream():
            yield f"data: {json.dumps({'type':'done','citations': [], 'error': f'Retrieval service import failed: {exc}'})}\n\n"

        return StreamingResponse(err_stream(), media_type="text/event-stream")

    if not settings.openai_api_key:
        async def missing_key_stream():
            yield 'data: {"type": "done", "citations": [], "error": "OPENAI_API_KEY is missing in backend/.env"}\n\n'

        return StreamingResponse(missing_key_stream(), media_type="text/event-stream")

    async def event_generator():
        async for event in retrieval_service.stream_answer(request.question, request.session_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
