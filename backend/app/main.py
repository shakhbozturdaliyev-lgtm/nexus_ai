"""FastAPI application entrypoint for NEXUS AI."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import uuid
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import text
from backend.app.api.ai_settings import router as ai_settings_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.audit_logs import router as audit_logs_router
from backend.app.api.auth import router as auth_router
from backend.app.api.business import router as business_router
from backend.app.api.conversations import router as conversations_router
from backend.app.api.knowledge import router as knowledge_router
from backend.app.api.orders import router as orders_router
from backend.app.api.products import router as products_router
from backend.app.api.tickets import router as tickets_router
from backend.app.api.users import router as users_router
from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.logging import logger
from backend.app.database.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager: runs schema init & seed on startup."""
    logger.info("Initializing NEXUS AI backend application...")
    try:
        await seed_data()
        logger.info("Database initialized and ready.")
    except Exception as e:
        logger.error(f"Error during startup database initialization: {e}")
    yield
    logger.info("Shutting down NEXUS AI backend application...")


app = FastAPI(
    title="NEXUS AI Platform",
    description="Intelligent Multilingual Customer Support Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Correlation ID attachment and structured request timing middleware."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response: Response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# Mount API Routers
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(tickets_router)
app.include_router(knowledge_router)
app.include_router(ai_settings_router)
app.include_router(analytics_router)
app.include_router(users_router)
app.include_router(business_router)
app.include_router(audit_logs_router)


@app.get("/api/health", tags=["System"])
async def health_check():
    """Liveness probe: verifies service process is running."""
    return {
        "status": "ok",
        "service": "NEXUS AI",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@app.get("/api/ready", tags=["System"])
async def readiness_check():
    """Readiness probe: verifies database connectivity."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                return {
                    "status": "ready",
                    "database": "connected",
                    "default_business_id": settings.default_business_id,
                }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "database": "disconnected", "error": str(e)},
        )


# Mount React Admin Frontend if dist exists
_frontend_dist = Path("/app/frontend/dist")
if not _frontend_dist.exists():
    _frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if _frontend_dist.exists() and (_frontend_dist / "index.html").is_file():
    if (_frontend_dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="static_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Exclude API endpoints, Swagger docs, and health checks
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        target_file = _frontend_dist / full_path
        if full_path and target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(_frontend_dist / "index.html")
