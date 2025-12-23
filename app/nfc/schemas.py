from pydantic import BaseModel

class NFCResolveRequest(BaseModel):
    tag_id: str

class NFCResolveResponse(BaseModel):
    patient_id: str
    organization_id: str
