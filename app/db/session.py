"""
Database Session Management

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Handles SQLAlchemy session creation and management with multi-tenant schema support.
    Provides per-organization database isolation through PostgreSQL schemas.
"""

import os
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db_for_org(organization_id: str, schema_name: Optional[str] = None):
    db = SessionLocal()
    if not schema_name:
        schema_name = db.execute(
            text(
                """
                SELECT schema_name
                FROM wailsalutem.organizations
                WHERE id = :org_id
                """
            ),
            {"org_id": organization_id},
        ).scalar()

    if not schema_name:
        db.close()
        raise RuntimeError("Schema name not found for organization")

    db.connection().exec_driver_sql(f'SET search_path TO "{schema_name}"')
    result = db.execute(text("SHOW search_path")).fetchone()
    print("SEARCH PATH:", result)

    return db



