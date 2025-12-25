from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.db.session import get_db_for_org
from app.db.models import NFCTag
from app.nfc.schemas import NFCResolveRequest, NFCResolveResponse
from app.messaging.rabbitmq import publish_event

router = APIRouter(prefix="/nfc", tags=["NFC"])

@router.post(
    "/resolve",
    response_model=NFCResolveResponse,
)
def resolve_nfc_tag(
    payload: NFCResolveRequest,
    user=Depends(require_role(["CAREGIVER"])),
):
    organization_id = user["organization_id"]

    db = next(get_db_for_org(organization_id))

    try:
        result = db.execute(
            text(f'SELECT id, tag_id, patient_id, status FROM "{organization_id}".nfc_tags WHERE tag_id = :tag_id'),
            {"tag_id": payload.tag_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="NFC tag not found")

        tag_id, patient_id, status = result.tag_id, result.patient_id, result.status

        if status != "active":
            raise HTTPException(status_code=403, detail="NFC tag is not active")
        
        publish_event(
            routing_key="nfc.resolved",
            payload={
            "event": "nfc.resolved",
                "tag_id": payload.tag_id,
                "patient_id": str(patient_id),
                "organization_id": organization_id,
                "caregiver_id": user["user_id"],  # Keycloak user id
            },
    )


        return NFCResolveResponse(
            patient_id=str(patient_id),
            organization_id=organization_id,
        )
    finally:
        db.close()
