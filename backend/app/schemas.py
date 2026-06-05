from pydantic import BaseModel, Field, HttpUrl


class IngestRequest(BaseModel):
    youtube_url: HttpUrl
    instagram_url: HttpUrl


class VideoMetadata(BaseModel):
    video_id: str
    platform: str
    url: str
    creator: str = "unknown"
    follower_count: int | None = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    hashtags: list[str] = Field(default_factory=list)
    upload_date: str | None = None
    duration_seconds: float | None = None
    transcript: str
    engagement_rate: float


class IngestResponse(BaseModel):
    videos: list[VideoMetadata]


class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"


class Citation(BaseModel):
    video_id: str
    platform: str
    chunk_index: int
    source_url: str


class ChatDonePayload(BaseModel):
    type: str = "done"
    citations: list[Citation]
