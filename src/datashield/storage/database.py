"""Database models and session management."""

from typing import Optional, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, Index
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class ScanSession(Base):
    """Database model for scan sessions."""

    __tablename__ = "scan_sessions"

    id = Column(String(36), primary_key=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    target_path = Column(String(500), nullable=False)
    mode = Column(String(20), default="safe")
    status = Column(String(20), default="running")  # running, paused, completed, failed
    total_files = Column(Integer, default=0)
    files_scanned = Column(Integer, default=0)
    findings_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    __table_args__ = (Index("idx_start_time", "start_time"),)


class Finding(Base):
    """Database model for findings."""

    __tablename__ = "findings"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), nullable=False)
    file_path = Column(String(500), nullable=False)
    pattern_name = Column(String(100), nullable=False)
    match_text = Column(String(500), nullable=True)
    risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    is_false_positive = Column(Boolean, default=False)
    encrypted = Column(Boolean, default=False)
    found_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index("idx_session_id", "session_id"),
        Index("idx_file_path", "file_path"),
    )


class VaultEntry(Base):
    """Database model for vault entries."""

    __tablename__ = "vault_entries"

    id = Column(String(36), primary_key=True)
    finding_id = Column(String(36), nullable=False)
    encrypted_value = Column(Text, nullable=False)
    iv = Column(String(32), nullable=False)
    tag = Column(String(32), nullable=False)
    encrypted_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("idx_finding_id", "finding_id"),)


def init_db(database_url: str = "sqlite:///datashield.db") -> sessionmaker:
    """Initialize database and return session factory.

    Args:
        database_url: Database connection URL.

    Returns:
        SQLAlchemy session factory.
    """
    if database_url.startswith("sqlite:///:memory:"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(database_url, pool_pre_ping=True)

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def get_session(SessionLocal: sessionmaker) -> Session:
    """Get a new database session."""
    return SessionLocal()
