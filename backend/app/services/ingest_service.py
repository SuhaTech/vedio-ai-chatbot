from __future__ import annotations

import json
import math
import time
import hashlib
from pathlib import Path
from typing import List

from openai import OpenAI

from app.core.config import settings
from app.schemas import VideoMetadata
from app.services.platform_service import extract_video_data


class IngestionService:
    def __init__(self) -> None:
        self.metadata_path = Path(settings.video_metadata_path)
        self.vectors_path = Path("./video_vectors.json")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def _load_metadata(self) -> dict:
        if not self.metadata_path.exists():
            return {}
        return json.loads(self.metadata_path.read_text(encoding="utf-8"))

    def _save_metadata(self, payload: dict) -> None:
        self.metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load_vectors(self) -> List[dict]:
        if not self.vectors_path.exists():
            return []
        return json.loads(self.vectors_path.read_text(encoding="utf-8"))

    def _save_vectors(self, vectors: List[dict]) -> None:
        self.vectors_path.write_text(json.dumps(vectors, indent=2), encoding="utf-8")

    @staticmethod
    def _engagement_rate(likes: int, comments: int, views: int) -> float:
        if views <= 0:
            return 0.0
        return round(((likes + comments) / views) * 100, 4)

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500) -> List[str]:
        words = text.split()
        chunks = []
        cur = []
        cur_len = 0
        for w in words:
            cur.append(w)
            cur_len += len(w) + 1
            if cur_len >= chunk_size:
                chunks.append(" ".join(cur))
                cur = []
                cur_len = 0
        if cur:
            chunks.append(" ".join(cur))
        return chunks

    def _embed_text(self, text: str) -> list[float]:
        # Call OpenAI embeddings API
        if not settings.openai_api_key:
            return self._fallback_embedding(text)
        try:
            resp = self.client.embeddings.create(model=settings.embedding_model, input=text)
            return resp.data[0].embedding
        except Exception:
            return self._fallback_embedding(text)

    @staticmethod
    def _fallback_embedding(text: str, dimensions: int = 256) -> list[float]:
        vector = [0.0] * dimensions
        tokens = text.lower().split()
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm > 0:
            vector = [value / norm for value in vector]
        return vector

    def ingest(self, youtube_url: str, instagram_url: str) -> List[VideoMetadata]:
        metadata_store = self._load_metadata()
        vectors = self._load_vectors()
        results: List[VideoMetadata] = []

        for label, url in [("A", youtube_url), ("B", instagram_url)]:
            raw = extract_video_data(url, video_id=label)
            engagement = self._engagement_rate(raw.get("likes", 0), raw.get("comments", 0), raw.get("views", 0))

            record = VideoMetadata(
                video_id=label,
                platform=raw.get("platform", "unknown"),
                url=raw.get("url", url),
                creator=raw.get("creator", "unknown"),
                follower_count=raw.get("follower_count"),
                views=raw.get("views", 0),
                likes=raw.get("likes", 0),
                comments=raw.get("comments", 0),
                hashtags=raw.get("hashtags", []),
                upload_date=raw.get("upload_date"),
                duration_seconds=raw.get("duration_seconds"),
                transcript=raw.get("transcript", ""),
                engagement_rate=engagement,
            )
            results.append(record)

            metadata_store[label] = record.model_dump()

            # chunk transcript and embed
            chunks = self._chunk_text(record.transcript or "")
            for idx, chunk in enumerate(chunks):
                try:
                    emb = self._embed_text(chunk)
                except Exception:
                    emb = []
                vectors.append({
                    "id": f"{label}-{idx}",
                    "video_id": label,
                    "chunk_index": idx,
                    "text": chunk,
                    "embedding": emb,
                    "source_url": record.url,
                })
                # rate limit pause
                time.sleep(0.1)

        self._save_metadata(metadata_store)
        self._save_vectors(vectors)
        return results


ingestion_service = IngestionService()
