"""
FastAPI backend wrapping the Dealmaker agent.

Endpoints:
  GET  /api/health        → { "status": "ok" }
  POST /api/dealmaker     → DealOutput

Run:
  uvicorn dealmaker_api:app --reload --port 8000
"""

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure the parent directory is on sys.path so dealmaker can import config
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dealmaker import run_deal, DealOutput  # noqa: E402

# ──────────────────────────────────────────────────────────────
#  FastAPI app
# ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Dealmaker API",
    description="Alternative energy supplier recommendation engine for India",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────
#  Request / Response schemas
# ──────────────────────────────────────────────────────────────

class DealmakerRequest(BaseModel):
    resource: str
    shortage_amount: str


# ──────────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/dealmaker", response_model=DealOutput)
def dealmaker(body: DealmakerRequest):
    """
    Run the Dealmaker agent to find alternative supplier countries
    for a given resource shortage.
    """
    try:
        result = run_deal(body.resource, body.shortage_amount)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {exc}",
        )

    if result.error:
        raise HTTPException(
            status_code=502,
            detail=result.recommendation_reason,
        )

    return result
