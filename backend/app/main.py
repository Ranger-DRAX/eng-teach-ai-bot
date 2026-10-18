"""FastAPI application entry point. Updated for live Gemini 2.5."""

from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base
from app.routes import children, dashboard, health, sessions

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Application startup and shutdown lifecycle."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logger.info("Application starting (env=%s)", settings.app_env)

    # Automatically ensure schema tables exist for local development / testing
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized")
    except Exception as exc:
        logger.warning("Database schema auto-creation skipped or deferred: %s", exc)

    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="English Learning Chatbot API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    """Inject a correlation ID into each request for structured logging."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# Register route modules
app.include_router(health.router, tags=["health"])
app.include_router(children.router, prefix="/api/v1", tags=["children"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
