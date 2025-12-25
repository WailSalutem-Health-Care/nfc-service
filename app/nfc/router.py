from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from app.auth.dependencies import require_permission_any
from app.db.session import get_db_for_org
from app.nfc.schemas import NFCResolveRequest, NFCResolveResponse, NFCDeactivateRequest
from app.messaging.rabbitmq import publish_event

router = APIRouter(prefix="/nfc", tags=["NFC"])


@router.post(
    "/resolve",
    response_model=NFCResolveResponse,
)
def resolve_nfc_tag(
    payload: NFCResolveRequest,
    user=Depends(require_permission_any([
        "nfc:check-in",
        "nfc:check-out",
    ])),
):
    org_id = user["organization_id"]
    db = next(get_db_for_org(org_id))

    try:
        result = db.execute(
            text(
                f'''
                SELECT tag_id, patient_id, status
                FROM "{org_id}".nfc_tags
                WHERE tag_id = :tag_id
                '''
            ),
            {"tag_id": payload.tag_id},
        ).fetchone()

        if not result:
            raise HTTPException(404, "NFC tag not found")

        if result.status != "active":
            raise HTTPException(403, "NFC tag is not active")

        publish_event(
            routing_key="nfc.resolved",
            payload={
                "event": "nfc.resolved",
                "tag_id": payload.tag_id,
                "patient_id": str(result.patient_id),
                "organization_id": org_id,
                "caregiver_id": user["user_id"],
            },
        )

        return NFCResolveResponse(
            patient_id=str(result.patient_id),
            organization_id=org_id,
        )

    finally:
        db.close()


