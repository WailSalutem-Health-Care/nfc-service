from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import require_permission_any
from app.db.session import get_db_for_org
from app.messaging.rabbitmq import publish_event
from app.nfc.repositories import NfcRepository
from app.nfc.schemas import (
    NFCAssignRequest,
    NFCAssignResponse,
    NFCDeactivateRequest,
    NFCDeactivateResponse,
    NFCGetResponse,
    NFCListResponse,
    NFCReactivateRequest,
    NFCReactivateResponse,
    NFCReplaceRequest,
    NFCReplaceResponse,
    NFCResolveRequest,
    NFCResolveResponse,
    NFCStatsResponse,
)
from app.nfc.services import NfcService


router = APIRouter(prefix="/nfc", tags=["NFC"])


@router.post(
    "/resolve",
    response_model=NFCResolveResponse,
)
def resolve_nfc_tag(
    payload: NFCResolveRequest,
    user=Depends(
        require_permission_any(
            [
                "nfc:resolve",
            ]
        )
    ),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.resolve_tag(
            organization_id=org_id,
            tag_id=payload.tag_id,
        )

        return NFCResolveResponse(**result)

    finally:
        db.close()


@router.get(
    "/patient/{patient_id}",
    response_model=NFCGetResponse,
)
def get_nfc_tag_by_patient(
    patient_id: str,
    user=Depends(require_permission_any(["nfc:read"])),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.get_tag_by_patient(
            organization_id=org_id,
            patient_id=patient_id,
        )

        return NFCGetResponse(**result)

    finally:
        db.close()


@router.get(
    "/",
    response_model=NFCListResponse,
)
def get_all_nfc_tags(
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user=Depends(require_permission_any(["nfc:read"])),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.get_all_tags(
            organization_id=org_id,
            limit=limit,
            cursor=cursor,
            status=status,
            search=search,
        )

        return NFCListResponse(**result)

    finally:
        db.close()


@router.get(
    "/stats",
    response_model=NFCStatsResponse,
)
def get_nfc_stats(
    user=Depends(require_permission_any(["nfc:read"])),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.get_stats()

        return NFCStatsResponse(**result)

    finally:
        db.close()


@router.get(
    "/{tag_id}",
    response_model=NFCGetResponse,
)
def get_nfc_tag(
    tag_id: str,
    user=Depends(require_permission_any(["nfc:read"])),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.get_tag(
            organization_id=org_id,
            tag_id=tag_id,
        )

        return NFCGetResponse(**result)

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
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.assign_tag(
            organization_id=org_id,
            user_id=user["user_id"],
            tag_id=payload.tag_id,
            patient_id=payload.patient_id,
        )

        return NFCAssignResponse(**result)

    finally:
        db.close()


@router.post(
    "/deactivate",
    response_model=NFCDeactivateResponse,
)
def deactivate_nfc_tag(
    payload: NFCDeactivateRequest,
    user=Depends(require_permission_any(["nfc:update"])),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.deactivate_tag(
            organization_id=org_id,
            tag_id=payload.tag_id,
        )

        return NFCDeactivateResponse(**result)

    finally:
        db.close()


@router.post(
    "/reactivate",
    response_model=NFCReactivateResponse,
)
def reactivate_nfc_tag(
    payload: NFCReactivateRequest,
    user=Depends(require_permission_any(["nfc:update"])),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.reactivate_tag(
            organization_id=org_id,
            tag_id=payload.tag_id,
        )

        return NFCReactivateResponse(**result)

    finally:
        db.close()


@router.post(
    "/replace",
    response_model=NFCReplaceResponse,
)
def replace_nfc_tag(
    payload: NFCReplaceRequest,
    user=Depends(require_permission_any(["nfc:update"])),
):
    org_id = user["organization_id"]
    db = get_db_for_org(org_id, user.get("schema_name"))

    try:
        repository = NfcRepository(db)
        service = NfcService(repository, publish_event)

        result = service.replace_tag(
            organization_id=org_id,
            old_tag_id=payload.old_tag_id,
            new_tag_id=payload.new_tag_id,
        )

        return NFCReplaceResponse(**result)

    finally:
        db.close()
