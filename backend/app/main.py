"""FastAPI application factory."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import logger
from app.db.session import init_db, close_db
from app.ai.rag.cache import cleanup_cache_periodically

settings = get_settings()


# Startup and shutdown events
async def startup_event():
    """Application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
    
    # Start cache cleanup task
    asyncio.create_task(cache_cleanup_loop())


async def shutdown_event():
    """Application shutdown."""
    logger.info("Shutting down application")
    await close_db()


async def cache_cleanup_loop():
    """Periodically clean up expired cache entries."""
    while True:
        try:
            await asyncio.sleep(300)  # Every 5 minutes
            await cleanup_cache_periodically()
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Multi-tenant AI Voice Agent Backend API",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and include routers
    from app.api.routes import (
        health,
        tenants,
        agents,
        chat,
        voice,
        knowledge
    )
    
    app.include_router(health.router)
    app.include_router(tenants.router)
    app.include_router(agents.router)
    app.include_router(chat.router)
    app.include_router(voice.router)
    app.include_router(knowledge.router)
    
    logger.info(f"FastAPI application created with {len(app.routes)} routes")
    
    return app


# Create the app instance
app = create_app()
