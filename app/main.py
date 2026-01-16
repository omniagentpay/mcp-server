import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import structlog
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.lifecycle import startup_event, shutdown_event
from app.mcp.router import router as mcp_router
from app.webhooks.circle import router as circle_webhook_router
from app.db.session import engine
import app.mcp.tools    # Register payment tools

setup_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event(app)
    yield
    await engine.dispose()
    await shutdown_event(app)

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Middleware for Correlation ID and Request Logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(
        "http_request",
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=process_time
    )
    return response

# Global Exception Handler for Production Hardening
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact support."},
    )

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(mcp_router, prefix=f"{settings.API_V1_STR}/mcp", tags=["mcp"])
app.include_router(circle_webhook_router, prefix=f"{settings.API_V1_STR}/webhooks", tags=["webhooks"])

@app.get("/health")
async def health_check():
    """Enhanced health check with DB connectivity verification."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": "disconnected"}
        )
