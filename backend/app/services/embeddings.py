from __future__ import annotations

import hashlib
import numpy as np


VECTOR_SIZE = 384


def _seed_from_text(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def embed_text(text: str) -> list[float]:
    # deterministic fallback embedding (keeps service functional without heavy local model)
    rs = np.random.default_rng(_seed_from_text(text))
    vec = rs.standard_normal(VECTOR_SIZE)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec.tolist()
    return (vec / norm).tolist()


def embed_many(texts: list[str]) -> list[list[float]]:
    return [embed_text(t) for t in texts]
