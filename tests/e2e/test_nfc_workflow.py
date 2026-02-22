"""
End-to-End Tests for NFC Workflow

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    End-to-end tests for complete NFC tag workflows.
    Tests the entire flow from tag assignment to deactivation with real database operations.
"""

import sqlite3
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.nfc.router as nfc_router
from app.auth.dependencies import get_current_user
from app.main import app, consumer


@pytest.fixture()
def e2e_client(tmp_path, monkeypatch):
    sqlite3.register_adapter(UUID, str)
    monkeypatch.setenv("RABBITMQ_CONSUMER_ENABLED", "false")
    monkeypatch.setattr(consumer, "start", lambda: None)
    monkeypatch.setattr(consumer, "stop", lambda: None)

    db_path = tmp_path / "nfc_test.db"
    engine = create_engine(
        f"sqlite+pysqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    entity_id = "00000000-0000-0000-0000-000000000001"
    other_entity_id = "00000000-0000-0000-0000-000000000002"

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE patients (
                    id TEXT PRIMARY KEY
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE nfc_tags (
                    tag_id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    status TEXT,
                    issued_at TEXT,
                    deactivated_at TEXT
                )
                """
            )
        )
        conn.execute(text("INSERT INTO patients (id) VALUES (:id)"), {"id": entity_id})
        conn.execute(
            text("INSERT INTO patients (id) VALUES (:id)"),
            {"id": other_entity_id},
        )

    def _get_db_for_org(_organization_id: str, _schema_name: str | None = None):
        return SessionLocal()

    published_events = []

    def _publish_event(**kwargs):
        published_events.append(kwargs)

    monkeypatch.setattr(nfc_router, "get_db_for_org", _get_db_for_org)
    monkeypatch.setattr(nfc_router, "publish_event", _publish_event)

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "user-1",
        "organization_id": "org-1",
        "schema_name": None,
        "roles": ["ORG_ADMIN", "CAREGIVER"],
    }

    with TestClient(app) as client:
        yield client, published_events, entity_id, other_entity_id

    app.dependency_overrides.clear()


def test_nfc_workflow_assign_resolve_deactivate_reactivate_replace(e2e_client):
    client, published_events, entity_id, _other_entity_id = e2e_client

    response = client.post(
        "/nfc/assign",
        json={"tag_id": "tag-1", "patient_id": entity_id},
    )
    assert response.status_code == 201
    assert response.json() == {
        "tag_id": "tag-1",
        "patient_id": entity_id,
        "organization_id": "org-1",
        "status": "active",
    }

    response = client.post("/nfc/resolve", json={"tag_id": "tag-1"})
    assert response.status_code == 200
    assert response.json() == {
        "patient_id": entity_id,
        "organization_id": "org-1",
    }

    response = client.post("/nfc/deactivate", json={"tag_id": "tag-1"})
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    response = client.get("/nfc/tag-1")
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    response = client.post("/nfc/reactivate", json={"tag_id": "tag-1"})
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    response = client.post(
        "/nfc/replace",
        json={"old_tag_id": "tag-1", "new_tag_id": "tag-2"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    response = client.get("/nfc/tag-2")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    response = client.get("/nfc/tag-1")
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    assert [event["routing_key"] for event in published_events] == [
        "nfc.assigned",
        "nfc.resolved",
    ]


def test_get_all_invalid_status_returns_400(e2e_client):
    client, _published_events, _entity_id, _other_entity_id = e2e_client

    response = client.get("/nfc", params={"status": "pending"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status filter"


def test_replace_tag_conflict_returns_409(e2e_client):
    client, _published_events, entity_id, other_entity_id = e2e_client

    response = client.post(
        "/nfc/assign",
        json={"tag_id": "tag-1", "patient_id": entity_id},
    )
    assert response.status_code == 201

    response = client.post(
        "/nfc/assign",
        json={"tag_id": "tag-2", "patient_id": other_entity_id},
    )
    assert response.status_code == 201

    response = client.post(
        "/nfc/replace",
        json={"old_tag_id": "tag-1", "new_tag_id": "tag-2"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "New tag is assigned to a different patient"


def test_resolve_inactive_tag_returns_403(e2e_client):
    client, _published_events, entity_id, _other_entity_id = e2e_client

    response = client.post(
        "/nfc/assign",
        json={"tag_id": "tag-1", "patient_id": entity_id},
    )
    assert response.status_code == 201

    response = client.post("/nfc/deactivate", json={"tag_id": "tag-1"})
    assert response.status_code == 200

    response = client.post("/nfc/resolve", json={"tag_id": "tag-1"})
    assert response.status_code == 403
    assert response.json()["detail"] == "NFC tag is not active"
