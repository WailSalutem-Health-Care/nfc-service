"""
Integration Tests for NFC Router

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Integration tests for NFC API endpoints.
    Tests HTTP routing, request/response handling, and endpoint behavior.
"""

from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

import app.nfc.router as nfc_router
from app.auth.dependencies import get_current_user
from app.main import app, consumer


class _DummyDB:
    def close(self):
        pass


@pytest.fixture()
def client_with_service(monkeypatch):
    monkeypatch.setattr(consumer, "start", lambda: None)
    monkeypatch.setattr(consumer, "stop", lambda: None)

    service = Mock()

    monkeypatch.setattr(nfc_router, "get_db_for_org", lambda *_: _DummyDB())
    monkeypatch.setattr(nfc_router, "NfcRepository", lambda *_: object())
    monkeypatch.setattr(nfc_router, "NfcService", lambda *_: service)

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "user-1",
        "organization_id": "org-1",
        "schema_name": None,
        "roles": ["ORG_ADMIN", "CAREGIVER"],
    }

    with TestClient(app) as client:
        yield client, service

    app.dependency_overrides.clear()


def test_resolve_tag_endpoint(client_with_service):
    client, service = client_with_service
    service.resolve_tag.return_value = {
        "patient_id": "00000000-0000-0000-0000-000000000001",
        "organization_id": "org-1",
    }

    response = client.post("/nfc/resolve", json={"tag_id": "tag-1"})

    assert response.status_code == 200
    assert response.json() == service.resolve_tag.return_value
    service.resolve_tag.assert_called_once_with(
        organization_id="org-1",
        tag_id="tag-1",
    )


def test_assign_tag_endpoint(client_with_service):
    client, service = client_with_service
    service.assign_tag.return_value = {
        "tag_id": "tag-1",
        "patient_id": "00000000-0000-0000-0000-000000000001",
        "organization_id": "org-1",
        "status": "active",
    }

    response = client.post(
        "/nfc/assign",
        json={
            "tag_id": "tag-1",
            "patient_id": "00000000-0000-0000-0000-000000000001",
        },
    )

    assert response.status_code == 201
    assert response.json() == service.assign_tag.return_value
    service.assign_tag.assert_called_once_with(
        organization_id="org-1",
        user_id="user-1",
        tag_id="tag-1",
        patient_id=UUID("00000000-0000-0000-0000-000000000001"),
    )


def test_deactivate_tag_endpoint(client_with_service):
    client, service = client_with_service
    service.deactivate_tag.return_value = {
        "tag_id": "tag-1",
        "organization_id": "org-1",
        "status": "inactive",
    }

    response = client.post("/nfc/deactivate", json={"tag_id": "tag-1"})

    assert response.status_code == 200
    assert response.json() == service.deactivate_tag.return_value
    service.deactivate_tag.assert_called_once_with(
        organization_id="org-1",
        tag_id="tag-1",
    )


def test_reactivate_tag_endpoint(client_with_service):
    client, service = client_with_service
    service.reactivate_tag.return_value = {
        "tag_id": "tag-1",
        "organization_id": "org-1",
        "status": "active",
    }

    response = client.post("/nfc/reactivate", json={"tag_id": "tag-1"})

    assert response.status_code == 200
    assert response.json() == service.reactivate_tag.return_value
    service.reactivate_tag.assert_called_once_with(
        organization_id="org-1",
        tag_id="tag-1",
    )


def test_replace_tag_endpoint(client_with_service):
    client, service = client_with_service
    service.replace_tag.return_value = {
        "old_tag_id": "tag-1",
        "new_tag_id": "tag-2",
        "patient_id": "00000000-0000-0000-0000-000000000001",
        "organization_id": "org-1",
        "status": "active",
    }

    response = client.post(
        "/nfc/replace",
        json={"old_tag_id": "tag-1", "new_tag_id": "tag-2"},
    )

    assert response.status_code == 200
    assert response.json() == service.replace_tag.return_value
    service.replace_tag.assert_called_once_with(
        organization_id="org-1",
        old_tag_id="tag-1",
        new_tag_id="tag-2",
    )


def test_get_tag_endpoint(client_with_service):
    client, service = client_with_service
    service.get_tag.return_value = {
        "tag_id": "tag-1",
        "patient_id": "00000000-0000-0000-0000-000000000001",
        "organization_id": "org-1",
        "status": "active",
        "issued_at": None,
        "deactivated_at": None,
    }

    response = client.get("/nfc/tag-1")

    assert response.status_code == 200
    assert response.json() == service.get_tag.return_value
    service.get_tag.assert_called_once_with(
        organization_id="org-1",
        tag_id="tag-1",
    )


def test_get_tag_by_patient_endpoint(client_with_service):
    client, service = client_with_service
    service.get_tag_by_patient.return_value = {
        "tag_id": "tag-1",
        "patient_id": "00000000-0000-0000-0000-000000000001",
        "organization_id": "org-1",
        "status": "active",
        "issued_at": None,
        "deactivated_at": None,
    }

    response = client.get("/nfc/patient/00000000-0000-0000-0000-000000000001")

    assert response.status_code == 200
    assert response.json() == service.get_tag_by_patient.return_value
    service.get_tag_by_patient.assert_called_once_with(
        organization_id="org-1",
        patient_id="00000000-0000-0000-0000-000000000001",
    )


def test_get_all_tags_endpoint(client_with_service):
    client, service = client_with_service
    service.get_all_tags.return_value = {
        "items": [
            {
                "tag_id": "tag-1",
                "patient_id": "00000000-0000-0000-0000-000000000001",
                "organization_id": "org-1",
                "status": "active",
                "issued_at": None,
                "deactivated_at": None,
            }
        ],
        "next_cursor": "tag-1",
    }

    response = client.get(
        "/nfc",
        params={"limit": 10, "cursor": "tag-0", "status": "active", "search": "tag"},
    )

    assert response.status_code == 200
    assert response.json() == service.get_all_tags.return_value
    service.get_all_tags.assert_called_once_with(
        organization_id="org-1",
        limit=10,
        cursor="tag-0",
        status="active",
        search="tag",
    )


def test_get_stats_endpoint(client_with_service):
    client, service = client_with_service
    service.get_stats.return_value = {"total": 5, "active": 3, "inactive": 2}

    response = client.get("/nfc/stats")

    assert response.status_code == 200
    assert response.json() == service.get_stats.return_value
    service.get_stats.assert_called_once_with()
