from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()

# Ensure async driver is used
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"Using Database URL: {database_url}")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Create session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Create base for models
Base = declarative_base()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection."""
    await engine.dispose()
