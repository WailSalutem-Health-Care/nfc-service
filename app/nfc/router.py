from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text

from app.auth.dependencies import require_permission_any
from app.db.session import get_db_for_org
from app.nfc.schemas import NFCResolveRequest, NFCResolveResponse
from app.messaging.rabbitmq import publish_event
from app.nfc.schemas import NFCAssignRequest, NFCAssignResponse


router = APIRouter(prefix="/nfc", tags=["NFC"])


@router.post(
    "/resolve",
    response_model=NFCResolveResponse,
)
def resolve_nfc_tag(
    payload: NFCResolveRequest,
    user=Depends(require_permission_any([
        "nfc:resolve",
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




@router.post(
    "/assign",
    response_model=NFCAssignResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_nfc_tag(
    payload: NFCAssignRequest,
    user=Depends(require_permission_any(["nfc:assign"])),
):
    org_id = user["organization_id"]
    db = next(get_db_for_org(org_id))

    try:
        # 1 Ensure patient exists
        patient = db.execute(
            text(
                f'''
                SELECT id
                FROM "{org_id}".patients
                WHERE id = :patient_id
                '''
            ),
            {"patient_id": payload.patient_id},
        ).fetchone()

        if not patient:
            raise HTTPException(404, "Patient not found")

        # 2️ Upsert NFC tag
        db.execute(
            text(
                f'''
                INSERT INTO "{org_id}".nfc_tags (tag_id, patient_id, status)
                VALUES (:tag_id, :patient_id, 'active')
                ON CONFLICT (tag_id)
                DO UPDATE SET
                    patient_id = EXCLUDED.patient_id,
                    status = 'active'
                '''
            ),
            {
                "tag_id": payload.tag_id,
                "patient_id": payload.patient_id,
            },
        )

        db.commit()

        # 3️ Publish assignment event 
        publish_event(
            routing_key="nfc.assigned",
            payload={
                "event": "nfc.assigned",
                "tag_id": payload.tag_id,
                "patient_id": str(payload.patient_id),
                "organization_id": org_id,
                "assigned_by": user["user_id"],
            },
        )

        return NFCAssignResponse(
            tag_id=payload.tag_id,
            patient_id=payload.patient_id,
            organization_id=org_id,
            status="active",
        )

    finally:
        db.close()
