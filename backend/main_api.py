"""
main_api.py — FastAPI server that runs the full pipeline once at startup
and serves cached results via REST endpoints.

This file does NOT modify main.py — it only imports agent functions,
runs them on server startup (via lifespan), and stores the results in
memory for fast read-only endpoints.
"""

from __future__ import annotations

import contextlib
import io
import logging
import os
import sys
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Force UTF-8 on stdout/stderr so pipeline agents that print Unicode
# box-drawing characters (Dealmaker) don't crash with a UnicodeEncodeError
# on Windows (cp1252).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import numpy as np

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

# ── Pipeline imports (identical order / structure to main.py) ────────────
from scout.scout import run_scout
from accountant import run_accountant
from strategist import run_strategist
from allocator import run_allocator

# ``dealmaker.py`` lives inside the backend/dealmaker directory.  Put that
# directory ahead of the project root so this imports the module, rather than
# the directory itself (exact same pattern as main.py).
DEALMAKER_DIR = Path(__file__).resolve().parent / "dealmaker"
sys.path.insert(0, str(DEALMAKER_DIR))
from dealmaker import run_dealmaker

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main_api")

# ── Global pipeline state ────────────────────────────────────────────────
# This dict is the single source of truth for all cached agent outputs.
# It is populated once on startup (background thread) and read by the
# REST endpoints.
PIPELINE_STATE: dict[str, Any] = {
    # Start as "running" immediately — the pipeline thread is already
    # dispatched during the lifespan phase, so there is no "idle" window.
    "status": "running",
    "last_run_at": None,
    "error": None,
    "scout": None,
    "accountant": None,
    "strategist": None,
    "allocator": None,
    "dealmaker": None,
    "navigator": None,
}

_lock = threading.Lock()


def _ensure_json_safe(obj: Any) -> Any:
    """Recursively convert an object to a JSON-safe Python type.

    Handles numpy scalars, arrays, and other non-serialisable types that
    pipeline agents (especially Accountant / Strategist / Allocator) may
    return, before FastAPI's own jsonable_encoder sees them.
    """
    # ── numpy scalars ───────────────────────────────────────────────
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.void):
        return None

    # ── numpy arrays ────────────────────────────────────────────────
    if isinstance(obj, np.ndarray):
        return _ensure_json_safe(obj.tolist())

    # ── pandas Timestamp / Timedelta ────────────────────────────────
    # (pandas is a transitive dependency, so it may be available)
    _pandas = sys.modules.get("pandas")
    if _pandas is not None:
        if isinstance(obj, _pandas.Timestamp):
            return obj.isoformat()
        if isinstance(obj, _pandas.Timedelta):
            return str(obj)

    # ── collections ─────────────────────────────────────────────────
    if isinstance(obj, dict):
        return {k: _ensure_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_ensure_json_safe(v) for v in obj]

    # ── let FastAPI's encoder handle Pydantic models, datetimes, etc.
    return jsonable_encoder(obj)


@contextlib.contextmanager
def _clean_argv_for_dealmaker():
    """Temporarily replace sys.argv so argparse-based functions like
    run_dealmaker() don't choke on uvicorn's CLI arguments."""
    original_argv = sys.argv[:]
    sys.argv = [sys.argv[0]]  # keep only the script name
    try:
        yield
    finally:
        sys.argv = original_argv


def run_pipeline() -> None:
    """Execute the full pipeline ONCE and write every result into PIPELINE_STATE.

    This function is intended to be called from a background thread so the
    ASGI server can start accepting requests immediately.
    """
    global PIPELINE_STATE

    with _lock:
        PIPELINE_STATE["error"] = None

    try:
        # ── 1. Scout ────────────────────────────────────────────────
        logger.info("=" * 60)
        logger.info("  Pipeline step 1/5 — Scout Agent")
        logger.info("=" * 60)
        scout_output = run_scout()
        with _lock:
            PIPELINE_STATE["scout"] = _ensure_json_safe(scout_output)
        logger.info("  ✓ Scout Agent completed")

        # ── 2. Accountant ───────────────────────────────────────────
        logger.info("=" * 60)
        logger.info("  Pipeline step 2/5 — Accountant Agent")
        logger.info("=" * 60)
        accountant_output = run_accountant(scout_output)
        with _lock:
            PIPELINE_STATE["accountant"] = _ensure_json_safe(accountant_output)
        logger.info("  ✓ Accountant Agent completed")

        # ── 3. Strategist ───────────────────────────────────────────
        logger.info("=" * 60)
        logger.info("  Pipeline step 3/5 — Strategist Agent")
        logger.info("=" * 60)
        strategist_output = run_strategist(scout_output, accountant_output)
        with _lock:
            PIPELINE_STATE["strategist"] = _ensure_json_safe(strategist_output)
        logger.info("  ✓ Strategist Agent completed")

        # ── 4. Allocator ────────────────────────────────────────────
        logger.info("=" * 60)
        logger.info("  Pipeline step 4/5 — Allocator Agent")
        logger.info("=" * 60)
        allocator_output = run_allocator(
            scout_output, accountant_output, strategist_output
        )
        with _lock:
            PIPELINE_STATE["allocator"] = _ensure_json_safe(allocator_output)
        logger.info("  ✓ Allocator Agent completed")

        # ── 5. Dealmaker (+ Navigator) ──────────────────────────────
        logger.info("=" * 60)
        logger.info("  Pipeline step 5/5 — Dealmaker / Navigator Agents")
        logger.info("=" * 60)
        # run_dealmaker() internally uses argparse and will choke on
        # uvicorn's CLI args in sys.argv — temporarily clean them.
        with _clean_argv_for_dealmaker():
            combined = run_dealmaker()
        with _lock:
            PIPELINE_STATE["dealmaker"] = _ensure_json_safe(combined["dealmaker"])
            PIPELINE_STATE["navigator"] = _ensure_json_safe(combined["navigator"])
        logger.info("  ✓ Dealmaker / Navigator Agents completed")

        # ── Mark ready ──────────────────────────────────────────────
        with _lock:
            PIPELINE_STATE["status"] = "ready"
            PIPELINE_STATE["last_run_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("=" * 60)
        logger.info("  Pipeline completed successfully at %s", PIPELINE_STATE["last_run_at"])
        logger.info("=" * 60)

    except Exception as e:
        logger.exception("Pipeline run failed: %s", str(e))
        with _lock:
            PIPELINE_STATE["status"] = "error"
            PIPELINE_STATE["error"] = str(e)


def _get_agent_output(key: str) -> Any:
    """Return stored output for *key*, or raise the right HTTPException."""
    with _lock:
        status = PIPELINE_STATE.get("status")
        value = PIPELINE_STATE.get(key)
        error_detail = PIPELINE_STATE.get("error")

    if status == "running":
        raise HTTPException(
            status_code=503,
            detail="Pipeline is still running, try again shortly",
        )
    if status == "error":
        raise HTTPException(
            status_code=500,
            detail=error_detail or "Unknown pipeline error",
        )
    return value


# ── FastAPI application ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle using the modern lifespan pattern.

    On startup we kick off the full pipeline in a **daemon background thread**
    so the server can start serving requests immediately while the pipeline
    executes in the background.
    """
    logger.info("Server starting — dispatching background pipeline run...")
    thread = threading.Thread(target=run_pipeline, daemon=True, name="pipeline-runner")
    thread.start()
    logger.info(
        "Background pipeline thread dispatched. "
        "Server is ready to serve requests (GET /api/health to check status)."
    )
    yield
    # Shutdown: nothing to clean up since the pipeline thread is a daemon.


app = FastAPI(
    title="Padava Processor API",
    description=(
        "Serves cached pipeline results from Scout, Accountant, Strategist, "
        "Allocator, Dealmaker, and Navigator agents. The pipeline runs "
        "automatically on server startup and results are served from memory."
    ),
    lifespan=lifespan,
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


# ── Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/health")
def health() -> dict[str, str]:
    """Return the current pipeline status (running / ready / error)."""
    with _lock:
        return {"status": PIPELINE_STATE["status"]}


@app.get("/api/scout")
def get_scout() -> Any:
    """Return the cached output from the Scout agent."""
    return _get_agent_output("scout")


@app.get("/api/accountant")
def get_accountant() -> Any:
    """Return the cached output from the Accountant agent."""
    return _get_agent_output("accountant")


@app.get("/api/strategist")
def get_strategist() -> Any:
    """Return the cached output from the Strategist agent."""
    return _get_agent_output("strategist")


@app.get("/api/allocator")
def get_allocator() -> Any:
    """Return the cached output from the Allocator agent."""
    return _get_agent_output("allocator")


@app.get("/api/dealmaker")
def get_dealmaker() -> Any:
    """Return the cached output from the Dealmaker agent."""
    return _get_agent_output("dealmaker")


@app.get("/api/navigator")
def get_navigator() -> Any:
    """Return the cached output from the Navigator agent."""
    return _get_agent_output("navigator")


# ── Optional: on-demand re-run ──────────────────────────────────────────

@app.post("/api/rerun")
def rerun_pipeline() -> dict[str, str]:
    """Re-trigger the full pipeline on demand (e.g. from a Refresh button).

    Returns immediately — the pipeline runs in the background.
    """
    with _lock:
        current_status = PIPELINE_STATE.get("status")

    if current_status == "running":
        raise HTTPException(
            status_code=409,
            detail="Pipeline is already running",
        )

    thread = threading.Thread(target=run_pipeline, daemon=True, name="pipeline-rerun")
    thread.start()
    logger.info("On-demand pipeline rerun triggered via POST /api/rerun")

    return {
        "status": "triggered",
        "detail": "Pipeline rerun started in background",
    }
