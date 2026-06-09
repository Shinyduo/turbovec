"""
TurboVec REST API wrapper.

TurboVec (https://github.com/RyanCodrai/turbovec) is an embedded vector search
library (Rust core + Python bindings) with no built-in server. This thin FastAPI
service exposes it as an HTTP API so it can be self-hosted on Railway:

  - add / search / delete vectors over HTTP
  - stable external uint64 IDs (IdMapIndex)
  - filtered (allowlist) search for hybrid retrieval
  - persistence to a mounted volume so the index survives restarts

Configuration via environment variables:
  INDEX_DIM        Vector dimensionality (default: 1536)
  INDEX_BIT_WIDTH  Quantization bit width: 2 or 4 (default: 4)
  DATA_DIR         Directory for the persisted index (default: /data)
  AUTO_SAVE        Persist after every mutation: true/false (default: true)
  API_KEY          If set, every request must send `X-API-Key: <value>`
  PORT             Port to listen on (Railway injects this; default 8080)
"""

import os
import threading
from typing import List, Optional

import numpy as np
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from turbovec import IdMapIndex

DIM = int(os.environ.get("INDEX_DIM", "1536"))
BIT_WIDTH = int(os.environ.get("INDEX_BIT_WIDTH", "4"))
DATA_DIR = os.environ.get("DATA_DIR", "/data")
AUTO_SAVE = os.environ.get("AUTO_SAVE", "true").lower() in ("1", "true", "yes")
API_KEY = os.environ.get("API_KEY", "").strip()

INDEX_PATH = os.path.join(DATA_DIR, "index.tvim")

_lock = threading.Lock()
_index: Optional[IdMapIndex] = None
_count = 0  # best-effort count of live vectors


def _new_index() -> IdMapIndex:
    return IdMapIndex(dim=DIM, bit_width=BIT_WIDTH)


def _save_locked() -> None:
    """Persist the index. Caller must hold _lock."""
    if _index is None:
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = INDEX_PATH + ".tmp"
    _index.write(tmp)
    os.replace(tmp, INDEX_PATH)


app = FastAPI(
    title="TurboVec API",
    description="HTTP wrapper around the TurboVec embedded vector search library.",
    version="1.0.0",
)


@app.on_event("startup")
def _startup() -> None:
    global _index
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(INDEX_PATH):
        _index = IdMapIndex.load(INDEX_PATH)
    else:
        _index = _new_index()


def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class AddRequest(BaseModel):
    vectors: List[List[float]] = Field(..., description="2D array of float vectors")
    ids: List[int] = Field(..., description="External uint64 ids, one per vector")


class SearchRequest(BaseModel):
    query: List[float] = Field(..., description="Single query vector")
    k: int = Field(10, ge=1, description="Number of nearest neighbours to return")
    allowlist: Optional[List[int]] = Field(
        None, description="Optional candidate id set to restrict the search to"
    )


class SearchHit(BaseModel):
    id: int
    score: float


class SearchResponse(BaseModel):
    results: List[SearchHit]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def info():
    return {
        "service": "turbovec-api",
        "dim": DIM,
        "bit_width": BIT_WIDTH,
        "count": _count,
        "auto_save": AUTO_SAVE,
        "persisted": os.path.exists(INDEX_PATH),
        "auth": bool(API_KEY),
    }


@app.post("/vectors", dependencies=[Depends(require_api_key)])
def add_vectors(req: AddRequest):
    global _count
    if len(req.vectors) != len(req.ids):
        raise HTTPException(400, "vectors and ids must have the same length")
    if not req.vectors:
        raise HTTPException(400, "no vectors provided")
    arr = np.asarray(req.vectors, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != DIM:
        raise HTTPException(
            400, f"each vector must have dimension {DIM}, got shape {list(arr.shape)}"
        )
    ids = np.asarray(req.ids, dtype=np.uint64)
    with _lock:
        _index.add_with_ids(arr, ids)
        _count += len(req.ids)
        if AUTO_SAVE:
            _save_locked()
    return {"added": len(req.ids), "count": _count}


@app.post("/search", response_model=SearchResponse, dependencies=[Depends(require_api_key)])
def search(req: SearchRequest):
    q = np.asarray(req.query, dtype=np.float32)
    if q.ndim != 1 or q.shape[0] != DIM:
        raise HTTPException(400, f"query must be a 1D vector of dimension {DIM}")
    # TurboVec expects a 2D batch of queries; send a single-row batch.
    queries = np.ascontiguousarray(q.reshape(1, DIM), dtype=np.float32)
    allow = (
        np.ascontiguousarray(np.asarray(req.allowlist, dtype=np.uint64))
        if req.allowlist is not None
        else None
    )
    with _lock:
        scores, ids = _index.search(queries, k=req.k, allowlist=allow)
    # Results come back as 2D (one row per query); take the first row.
    scores = np.asarray(scores).reshape(-1)
    ids = np.asarray(ids).reshape(-1)
    hits = [SearchHit(id=int(i), score=float(s)) for s, i in zip(scores, ids)]
    return SearchResponse(results=hits)


@app.delete("/vectors/{vector_id}", dependencies=[Depends(require_api_key)])
def remove_vector(vector_id: int):
    global _count
    with _lock:
        _index.remove(np.uint64(vector_id))
        _count = max(0, _count - 1)
        if AUTO_SAVE:
            _save_locked()
    return {"removed": vector_id, "count": _count}


@app.post("/save", dependencies=[Depends(require_api_key)])
def save():
    with _lock:
        _save_locked()
    return {"saved": True, "path": INDEX_PATH}


@app.post("/reset", dependencies=[Depends(require_api_key)])
def reset():
    """Drop all vectors and start a fresh empty index."""
    global _index, _count
    with _lock:
        _index = _new_index()
        _count = 0
        if AUTO_SAVE:
            _save_locked()
    return {"reset": True}
