from pydantic import BaseModel
from uuid import UUID

class NFCResolveRequest(BaseModel):
    tag_id: str

class NFCResolveResponse(BaseModel):
    patient_id: str
    organization_id: str

class NFCAssignRequest(BaseModel):
    tag_id: str
    patient_id: UUID


class NFCAssignResponse(BaseModel):
    tag_id: str
    patient_id: UUID
    organization_id: str
    status: str


class NFCDeactivateRequest(BaseModel):
    tag_id: str


class NFCDeactivateResponse(BaseModel):
    tag_id: str
    organization_id: str
    status: str


class NFCGetResponse(BaseModel):
    tag_id: str
    patient_id: str
    organization_id: str
    status: str
