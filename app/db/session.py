import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

def create_db_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}

    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        # On Vercel serverless filesystem, /var/task is read-only. Redirect SQLite to /tmp if fallback is used.
        if os.environ.get("VERCEL") and "./helplink.db" in db_url:
            db_url = "sqlite:////tmp/helplink.db"
    elif db_url.startswith("postgres://"):
        # Normalize legacy 'postgres://' scheme to SQLAlchemy 2.0 psycopg2 driver format
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://"):
        # Normalize standard 'postgresql://' scheme to SQLAlchemy 2.0 psycopg2 driver format
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        echo=False
    )

engine = create_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
