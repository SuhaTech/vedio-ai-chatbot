from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas import IngestRequest, IngestResponse, VideoMetadata

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    """
    Ingest endpoint supports a dev-mode fallback when `DEV_MODE` is true in config.
    This avoids importing heavy dependencies (langchain, chroma, numpy) during
    local UI testing. When not in dev mode, we lazily import the real ingestion
    service so missing packages raise normal errors.
    """
    if settings.dev_mode:
        # Lightweight mock response for quick frontend testing
        sample_a = VideoMetadata(
            video_id="A",
            platform="youtube",
            url=str(request.youtube_url),
            creator="Sample Creator A",
            follower_count=12345,
            views=10000,
            likes=1500,
            comments=120,
            hashtags=["#sample", "#demo"],
            upload_date="2024-01-01",
            duration_seconds=60,
            transcript="This is a sample transcript for video A. Hook: Amazing intro.",
            engagement_rate=round(((1500 + 120) / 10000) * 100, 4),
        )

        sample_b = VideoMetadata(
            video_id="B",
            platform="instagram",
            url=str(request.instagram_url),
            creator="Sample Creator B",
            follower_count=54321,
            views=8000,
            likes=600,
            comments=80,
            hashtags=["#reel", "#demo"],
            upload_date="2024-02-01",
            duration_seconds=30,
            transcript="This is a sample transcript for video B. Hook: Fast-paced start.",
            engagement_rate=round(((600 + 80) / 8000) * 100, 4),
        )

        return IngestResponse(videos=[sample_a, sample_b])

    # Not in dev mode: lazily import heavy ingestion service
    try:
        from app.services.ingest_service import ingestion_service
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion service missing or failed to import: {exc}")

    if not settings.openai_api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is missing in backend/.env")

    try:
        videos = ingestion_service.ingest(str(request.youtube_url), str(request.instagram_url))
        return IngestResponse(videos=videos)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
