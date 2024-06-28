"""Module for database connection."""


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

# PostgreSQL URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy setup
Base = declarative_base()

# Async engine instance
engine = create_async_engine(DATABASE_URL)

# Async session maker which is used as context manager for async queries
SessionLocal = async_sessionmaker(engine)
