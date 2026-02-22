"""
SQLAlchemy Database Models

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    SQLAlchemy ORM models for NFC tags and related entities.
    Defines database schema with timestamps and status tracking.
"""

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class NFCTag(Base):
    __tablename__ = "nfc_tags"
    __table_args__ = {"quote": True}

    id = Column(UUID, primary_key=True)
    tag_id = Column(String, nullable=False)
    patient_id = Column(UUID, nullable=False)
    status = Column(String, nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
