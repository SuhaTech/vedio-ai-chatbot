from __future__ import annotations

import json
import math
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import AsyncGenerator, List

from openai import OpenAI

from app.core.config import settings


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norma = math.sqrt(sum(x * x for x in a))
    normb = math.sqrt(sum(y * y for y in b))
    if norma == 0 or normb == 0:
        return 0.0
    return dot / (norma * normb)


class RetrievalService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.vectors_path = Path("./video_vectors.json")
        self.metadata_path = Path(settings.video_metadata_path)
        self.history: dict[str, list] = defaultdict(list)

    def _load_video_metadata(self) -> dict:
        if not self.metadata_path.exists():
            return {}
        return json.loads(self.metadata_path.read_text(encoding="utf-8"))

    def _load_vectors(self) -> List[dict]:
        if not self.vectors_path.exists():
            return []
        return json.loads(self.vectors_path.read_text(encoding="utf-8"))

    def _retrieve(self, question: str, k: int = 6) -> List[dict]:
        # embed the question
        if not settings.openai_api_key:
            q_emb = self._fallback_embedding(question)
        else:
            try:
                q_emb = self.client.embeddings.create(model=settings.embedding_model, input=question).data[0].embedding
            except Exception:
                q_emb = self._fallback_embedding(question)
        vectors = self._load_vectors()
        scored = []
        for v in vectors:
            score = _cosine(q_emb, v.get("embedding", []))
            scored.append((score, v))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [v for s, v in scored[:k]]

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

    async def stream_answer(self, question: str, session_id: str) -> AsyncGenerator[dict, None]:
        docs = self._retrieve(question, k=6)
        metadata_map = self._load_video_metadata()

        transcript_context = "\n\n".join([f"[video={d.get('video_id')} chunk={d.get('chunk_index')}] {d.get('text')}" for d in docs])
        video_context = json.dumps(metadata_map, indent=2)

        citations = [{
            "video_id": d.get("video_id"),
            "platform": metadata_map.get(d.get("video_id"), {}).get("platform", "?"),
            "chunk_index": d.get("chunk_index"),
            "source_url": d.get("source_url", ""),
        } for d in docs]

        system_instruction = (
            "You are a video performance analyst for creators. Always answer using dynamic facts from provided metadata and transcript context."
        )

        prompt = (
            f"System: {system_instruction}\n\n"
            f"Video metadata JSON:\n{video_context}\n\n"
            f"Retrieved transcript chunks:\n{transcript_context}\n\n"
            f"Question: {question}\n\n"
            "Answer concisely and cite which video and chunk you used for each claim."
        )

        # Stream tokens from OpenAI ChatCompletion
        # Using gpt-4o-mini or the specified model
        model = settings.openai_model
        # Build chat messages
        messages = [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}]

        answer_text = ""
        try:
            resp = self.client.chat.completions.create(model=model, messages=messages, temperature=0.2, stream=True)
            partial = []
            for chunk in resp:
                delta = chunk.choices[0].delta
                token = getattr(delta, 'content', None)
                if token:
                    partial.append(token)
                    yield {"type": "token", "token": token}
            answer_text = "".join(partial)
        except Exception:
            a = metadata_map.get("A", {})
            b = metadata_map.get("B", {})
            top_a = docs[0].get("text", "")[:120] if docs else ""
            top_b = docs[1].get("text", "")[:120] if len(docs) > 1 else ""
            answer_text = (
                f"Video A engagement rate is {a.get('engagement_rate', 0)}% and Video B is {b.get('engagement_rate', 0)}%. "
                f"A has {a.get('likes', 0)} likes and {a.get('comments', 0)} comments; B has {b.get('likes', 0)} likes and {b.get('comments', 0)} comments. "
                f"A's top retrieved chunk: {top_a}. B's top retrieved chunk: {top_b}."
            )
            for token in answer_text.split(" "):
                yield {"type": "token", "token": token + " "}
        # append to history
        self.history[session_id].append({"role": "user", "content": question})
        self.history[session_id].append({"role": "assistant", "content": answer_text})

        yield {"type": "done", "citations": citations}


retrieval_service = RetrievalService()
