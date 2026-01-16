from typing import List, Optional

from pydantic import BaseModel
from uuid import UUID


class NFCResolveRequest(BaseModel):
    tag_id: str


class NFCResolveResponse(BaseModel):
    id: str
    organization_id: str


class NFCAssignRequest(BaseModel):
    tag_id: str
    id: UUID


class NFCAssignResponse(BaseModel):
    tag_id: str
    id: UUID
    organization_id: str
    status: str


class NFCDeactivateRequest(BaseModel):
    tag_id: str


class NFCDeactivateResponse(BaseModel):
    tag_id: str
    organization_id: str
    status: str


class NFCReactivateRequest(BaseModel):
    tag_id: str


class NFCReactivateResponse(BaseModel):
    tag_id: str
    organization_id: str
    status: str


class NFCReplaceRequest(BaseModel):
    old_tag_id: str
    new_tag_id: str


class NFCReplaceResponse(BaseModel):
    old_tag_id: str
    new_tag_id: str
    id: UUID
    organization_id: str
    status: str


class NFCGetResponse(BaseModel):
    tag_id: str
    id: str
    organization_id: str
    status: str


class NFCListResponse(BaseModel):
    items: List[NFCGetResponse]
    next_cursor: Optional[str]


class NFCStatsResponse(BaseModel):
    total: int
    active: int
    inactive: int
