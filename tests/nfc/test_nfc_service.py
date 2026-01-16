import pytest
from fastapi import HTTPException
from types import SimpleNamespace
from unittest.mock import Mock

from app.nfc.services.nfc_service import NfcService


def make_service():
    repository = Mock()
    publisher = Mock()
    service = NfcService(repository, publisher)
    return service, repository, publisher


def test_resolve_tag_missing():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.resolve_tag("org-1", "tag-1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "NFC tag not found"


def test_resolve_tag_inactive():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=123,
        status="inactive",
    )

    with pytest.raises(HTTPException) as exc:
        service.resolve_tag("org-1", "tag-1")

    assert exc.value.status_code == 403
    assert exc.value.detail == "NFC tag is not active"


def test_resolve_tag_publishes_event():
    service, repository, publisher = make_service()
    repository.get_tag.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=123,
        status="active",
    )

    result = service.resolve_tag("org-1", "tag-1")

    publisher.assert_called_once_with(
        routing_key="nfc.resolved",
        payload={
            "event": "nfc.resolved",
            "tag_id": "tag-1",
            "patient_id": "123",
            "organization_id": "org-1",
        },
    )
    assert result == {
        "patient_id": "123",
        "organization_id": "org-1",
    }


def test_assign_tag_missing_patient():
    service, repository, _publisher = make_service()
    repository.get_patient.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.assign_tag("org-1", "user-1", "tag-1", 101)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Patient not found"


def test_assign_tag_conflict():
    service, repository, _publisher = make_service()
    repository.get_patient.return_value = SimpleNamespace(id=101)
    repository.get_active_tag_for_patient.return_value = SimpleNamespace(tag_id="tag-x")

    with pytest.raises(HTTPException) as exc:
        service.assign_tag("org-1", "user-1", "tag-1", 101)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Patient already has an active NFC tag"


def test_assign_tag_same_existing_tag_allows_update():
    service, repository, publisher = make_service()
    repository.get_patient.return_value = SimpleNamespace(id=101)
    repository.get_active_tag_for_patient.return_value = SimpleNamespace(tag_id="tag-1")

    result = service.assign_tag("org-1", "user-1", "tag-1", 101)

    repository.upsert_tag.assert_called_once_with("tag-1", 101)
    repository.commit.assert_called_once()
    publisher.assert_called_once_with(
        routing_key="nfc.assigned",
        payload={
            "event": "nfc.assigned",
            "tag_id": "tag-1",
            "patient_id": "101",
            "organization_id": "org-1",
            "assigned_by": "user-1",
        },
    )
    assert result == {
        "tag_id": "tag-1",
        "patient_id": 101,
        "organization_id": "org-1",
        "status": "active",
    }


def test_deactivate_tag_missing():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.deactivate_tag("org-1", "tag-1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "NFC tag not found"


def test_deactivate_tag_skips_if_already_inactive():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=101,
        status="inactive",
    )

    result = service.deactivate_tag("org-1", "tag-1")

    repository.deactivate_tag.assert_not_called()
    repository.commit.assert_not_called()
    assert result == {
        "tag_id": "tag-1",
        "organization_id": "org-1",
        "status": "inactive",
    }


def test_deactivate_tag_changes_status():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=101,
        status="active",
        issued_at=None,
        deactivated_at=None,
    )

    result = service.deactivate_tag("org-1", "tag-1")

    repository.deactivate_tag.assert_called_once_with("tag-1")
    repository.commit.assert_called_once()
    assert result == {
        "tag_id": "tag-1",
        "organization_id": "org-1",
        "status": "inactive",
    }


def test_reactivate_tag_missing():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.reactivate_tag("org-1", "tag-1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "NFC tag not found"


def test_reactivate_tag_skips_if_already_active():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=101,
        status="active",
    )

    result = service.reactivate_tag("org-1", "tag-1")

    repository.reactivate_tag.assert_not_called()
    repository.commit.assert_not_called()
    assert result == {
        "tag_id": "tag-1",
        "organization_id": "org-1",
        "status": "active",
    }


def test_reactivate_tag_changes_status():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=101,
        status="inactive",
    )

    result = service.reactivate_tag("org-1", "tag-1")

    repository.reactivate_tag.assert_called_once_with("tag-1")
    repository.commit.assert_called_once()
    assert result == {
        "tag_id": "tag-1",
        "organization_id": "org-1",
        "status": "active",
    }


def test_replace_tag_same_id_rejected():
    service, _repository, _publisher = make_service()

    with pytest.raises(HTTPException) as exc:
        service.replace_tag("org-1", "tag-1", "tag-1")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Old and new tag IDs must differ"


def test_replace_tag_missing_old_tag():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.replace_tag("org-1", "tag-1", "tag-2")

    assert exc.value.status_code == 404
    assert exc.value.detail == "NFC tag not found"


def test_replace_tag_conflict_on_new_tag():
    service, repository, _publisher = make_service()
    old_tag = SimpleNamespace(tag_id="tag-1", patient_id=101, status="active")
    repository.get_tag.side_effect = [old_tag, SimpleNamespace(tag_id="tag-2", patient_id=202, status="active")]

    with pytest.raises(HTTPException) as exc:
        service.replace_tag("org-1", "tag-1", "tag-2")

    assert exc.value.status_code == 409
    assert exc.value.detail == "New tag is assigned to a different patient"


def test_replace_tag_happy_path():
    service, repository, _publisher = make_service()
    old_tag = SimpleNamespace(tag_id="tag-1", patient_id=101, status="active")
    repository.get_tag.side_effect = [old_tag, None]

    result = service.replace_tag("org-1", "tag-1", "tag-2")

    repository.upsert_tag.assert_called_once_with("tag-2", 101)
    repository.deactivate_tag.assert_called_once_with("tag-1")
    repository.commit.assert_called_once()
    assert result == {
        "old_tag_id": "tag-1",
        "new_tag_id": "tag-2",
        "patient_id": 101,
        "organization_id": "org-1",
        "status": "active",
    }


def test_get_tag_missing():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_tag("org-1", "tag-1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "NFC tag not found"


def test_get_tag_success():
    service, repository, _publisher = make_service()
    repository.get_tag.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=101,
        status="active",
    )

    result = service.get_tag("org-1", "tag-1")

    assert result == {
        "tag_id": "tag-1",
        "patient_id": "101",
        "organization_id": "org-1",
        "status": "active",
        "issued_at": None,
        "deactivated_at": None,
    }


def test_get_tag_by_patient_missing():
    service, repository, _publisher = make_service()
    repository.get_tag_for_patient.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_tag_by_patient("org-1", 101)

    assert exc.value.status_code == 404
    assert exc.value.detail == "NFC tag not found"


def test_get_tag_by_patient_success():
    service, repository, _publisher = make_service()
    repository.get_tag_for_patient.return_value = SimpleNamespace(
        tag_id="tag-1",
        patient_id=101,
        status="active",
        issued_at=None,
        deactivated_at=None,
    )

    result = service.get_tag_by_patient("org-1", 101)

    assert result == {
        "tag_id": "tag-1",
        "patient_id": "101",
        "organization_id": "org-1",
        "status": "active",
        "issued_at": None,
        "deactivated_at": None,
    }


def test_get_all_tags_invalid_status():
    service, _repository, _publisher = make_service()

    with pytest.raises(HTTPException) as exc:
        service.get_all_tags("org-1", limit=10, cursor=None, status="pending", search=None)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid status filter"


def test_get_all_tags_paginates_and_normalizes_search():
    service, repository, _publisher = make_service()
    repository.get_all_tags.return_value = [
        SimpleNamespace(tag_id="tag-1", patient_id=101, status="active", issued_at=None, deactivated_at=None),
        SimpleNamespace(tag_id="tag-2", patient_id=102, status="inactive", issued_at=None, deactivated_at=None),
        SimpleNamespace(tag_id="tag-3", patient_id=103, status="active", issued_at=None, deactivated_at=None),
    ]

    result = service.get_all_tags("org-1", limit=2, cursor=None, status=None, search="  ")

    repository.get_all_tags.assert_called_once_with(
        limit=3,
        cursor=None,
        status=None,
        search=None,
    )
    assert result == {
        "items": [
            {
                "tag_id": "tag-1",
                "patient_id": "101",
                "organization_id": "org-1",
                "status": "active",
                "issued_at": None,
                "deactivated_at": None,
            },
            {
                "tag_id": "tag-2",
                "patient_id": "102",
                "organization_id": "org-1",
                "status": "inactive",
                "issued_at": None,
                "deactivated_at": None,
            },
        ],
        "next_cursor": "tag-2",
    }


def test_get_stats_defaults_to_zero():
    service, repository, _publisher = make_service()
    repository.get_stats.return_value = SimpleNamespace(total=None, active=None, inactive=None)

    result = service.get_stats()

    assert result == {
        "total": 0,
        "active": 0,
        "inactive": 0,
    }


def test_deactivate_tags_for_patient_commits():
    service, repository, _publisher = make_service()

    service.deactivate_tags_for_patient(101)

    repository.deactivate_tags_for_patient.assert_called_once_with(101)
    repository.commit.assert_called_once()


def test_deactivate_all_tags_commits():
    service, repository, _publisher = make_service()

    service.deactivate_all_tags()

    repository.deactivate_all_tags.assert_called_once_with()
    repository.commit.assert_called_once()
