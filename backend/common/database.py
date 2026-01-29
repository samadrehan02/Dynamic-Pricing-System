from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.common.config import settings

# ------------------------
# Engine
# ------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# ------------------------
# Session
# ------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ------------------------
# Base
# ------------------------
Base = declarative_base()

# ------------------------
# Dependency (FastAPI)
# ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
