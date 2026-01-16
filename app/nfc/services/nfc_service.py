from typing import Optional

from fastapi import HTTPException

from app.nfc.repositories import NfcRepository


class NfcService:
    def __init__(self, repository: NfcRepository, event_publisher):
        self._repository = repository
        self._publish_event = event_publisher

    def resolve_tag(self, organization_id: str, tag_id: str) -> dict:
        result = self._repository.get_tag(tag_id)

        if not result:
            raise HTTPException(404, "NFC tag not found")

        if result.status != "active":
            raise HTTPException(403, "NFC tag is not active")

        self._publish_event(
            routing_key="nfc.resolved",
            payload={
                "event": "nfc.resolved",
                "tag_id": tag_id,
                "id": str(result.patient_id),
                "organization_id": organization_id,
            },
        )

        return {
            "id": str(result.patient_id),
            "organization_id": organization_id,
        }

    def assign_tag(
        self,
        organization_id: str,
        user_id: str,
        tag_id: str,
        id,
    ) -> dict:
        patient = self._repository.get_patient(id)

        if not patient:
            raise HTTPException(404, "Patient not found")

        existing_tag = self._repository.get_active_tag_for_patient(id)

        if existing_tag and existing_tag.tag_id != tag_id:
            raise HTTPException(409, "Patient already has an active NFC tag")

        self._repository.upsert_tag(tag_id, id)
        self._repository.commit()

        self._publish_event(
            routing_key="nfc.assigned",
            payload={
                "event": "nfc.assigned",
                "tag_id": tag_id,
                "id": str(id),
                "organization_id": organization_id,
                "assigned_by": user_id,
            },
        )

        return {
            "tag_id": tag_id,
            "id": id,
            "organization_id": organization_id,
            "status": "active",
        }

    def deactivate_tag(self, organization_id: str, tag_id: str) -> dict:
        result = self._repository.get_tag(tag_id)

        if not result:
            raise HTTPException(404, "NFC tag not found")

        if result.status != "inactive":
            self._repository.deactivate_tag(tag_id)
            self._repository.commit()

        return {
            "tag_id": tag_id,
            "organization_id": organization_id,
            "status": "inactive",
        }

    def reactivate_tag(self, organization_id: str, tag_id: str) -> dict:
        result = self._repository.get_tag(tag_id)

        if not result:
            raise HTTPException(404, "NFC tag not found")

        if result.status != "active":
            self._repository.reactivate_tag(tag_id)
            self._repository.commit()

        return {
            "tag_id": tag_id,
            "organization_id": organization_id,
            "status": "active",
        }

    def replace_tag(
        self,
        organization_id: str,
        old_tag_id: str,
        new_tag_id: str,
    ) -> dict:
        if old_tag_id == new_tag_id:
            raise HTTPException(400, "Old and new tag IDs must differ")

        old_tag = self._repository.get_tag(old_tag_id)

        if not old_tag:
            raise HTTPException(404, "NFC tag not found")

        new_tag = self._repository.get_tag(new_tag_id)

        if new_tag and str(new_tag.patient_id) != str(old_tag.patient_id):
            raise HTTPException(409, "New tag is assigned to a different patient")

        self._repository.upsert_tag(new_tag_id, old_tag.patient_id)
        if old_tag.status != "inactive":
            self._repository.deactivate_tag(old_tag_id)
        self._repository.commit()

        return {
            "old_tag_id": old_tag_id,
            "new_tag_id": new_tag_id,
            "id": old_tag.patient_id,
            "organization_id": organization_id,
            "status": "active",
        }

    def get_tag(self, organization_id: str, tag_id: str) -> dict:
        result = self._repository.get_tag(tag_id)

        if not result:
            raise HTTPException(404, "NFC tag not found")

        return {
            "tag_id": result.tag_id,
            "id": str(result.patient_id),
            "organization_id": organization_id,
            "status": result.status,
        }

    def get_tag_by_id(self, organization_id: str, id) -> dict:
        result = self._repository.get_tag_for_patient(id)

        if not result:
            raise HTTPException(404, "NFC tag not found")

        return {
            "tag_id": result.tag_id,
            "id": str(result.patient_id),
            "organization_id": organization_id,
            "status": result.status,
        }

    def get_all_tags(
        self,
        organization_id: str,
        limit: int,
        cursor: Optional[str],
        status: Optional[str],
        search: Optional[str],
    ) -> dict:
        if status and status not in {"active", "inactive"}:
            raise HTTPException(400, "Invalid status filter")

        normalized_search = search.strip() if search else None
        if normalized_search == "":
            normalized_search = None

        fetch_limit = limit + 1
        results = self._repository.get_all_tags(
            limit=fetch_limit,
            cursor=cursor,
            status=status,
            search=normalized_search,
        )

        has_more = len(results) > limit
        trimmed = results[:limit]
        items = [
            {
                "tag_id": row.tag_id,
                "id": str(row.patient_id),
                "organization_id": organization_id,
                "status": row.status,
            }
            for row in trimmed
        ]
        next_cursor = trimmed[-1].tag_id if has_more and trimmed else None

        return {
            "items": items,
            "next_cursor": next_cursor,
        }

    def get_stats(self) -> dict:
        stats = self._repository.get_stats()
        return {
            "total": int(stats.total or 0),
            "active": int(stats.active or 0),
            "inactive": int(stats.inactive or 0),
        }

    def deactivate_tags_for_patient(self, patient_id):
        self._repository.deactivate_tags_for_patient(patient_id)
        self._repository.commit()

    def deactivate_all_tags(self):
        self._repository.deactivate_all_tags()
        self._repository.commit()
