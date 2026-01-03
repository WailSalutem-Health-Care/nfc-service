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
                "patient_id": str(result.patient_id),
                "organization_id": organization_id,
            },
        )

        return {
            "patient_id": str(result.patient_id),
            "organization_id": organization_id,
        }

    def assign_tag(
        self,
        organization_id: str,
        user_id: str,
        tag_id: str,
        patient_id,
    ) -> dict:
        patient = self._repository.get_patient(patient_id)

        if not patient:
            raise HTTPException(404, "Patient not found")

        existing_tag = self._repository.get_active_tag_for_patient(patient_id)

        if existing_tag and existing_tag.tag_id != tag_id:
            raise HTTPException(409, "Patient already has an active NFC tag")

        self._repository.upsert_tag(tag_id, patient_id)
        self._repository.commit()

        self._publish_event(
            routing_key="nfc.assigned",
            payload={
                "event": "nfc.assigned",
                "tag_id": tag_id,
                "patient_id": str(patient_id),
                "organization_id": organization_id,
                "assigned_by": user_id,
            },
        )

        return {
            "tag_id": tag_id,
            "patient_id": patient_id,
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

    def get_tag(self, organization_id: str, tag_id: str) -> dict:
        result = self._repository.get_tag(tag_id)

        if not result:
            raise HTTPException(404, "NFC tag not found")

        return {
            "tag_id": result.tag_id,
            "patient_id": str(result.patient_id),
            "organization_id": organization_id,
            "status": result.status,
        }

    def get_tag_by_patient(self, organization_id: str, patient_id) -> dict:
        result = self._repository.get_tag_for_patient(patient_id)

        if not result:
            raise HTTPException(404, "NFC tag not found")

        return {
            "tag_id": result.tag_id,
            "patient_id": str(result.patient_id),
            "organization_id": organization_id,
            "status": result.status,
        }

    def get_all_tags(self, organization_id: str, limit: int, cursor: Optional[str]) -> dict:
        fetch_limit = limit + 1
        results = self._repository.get_all_tags(limit=fetch_limit, cursor=cursor)

        has_more = len(results) > limit
        trimmed = results[:limit]
        items = [
            {
                "tag_id": row.tag_id,
                "patient_id": str(row.patient_id),
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
