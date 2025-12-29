from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.auth import decode_jwt
from app.auth.permissions import get_permissions_for_roles

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    payload = decode_jwt(credentials.credentials)

    user_id = payload.get("sub")
    organization_id = payload.get("organisationId")
    schema_name = payload.get("schema") or payload.get("schema_name")
    roles = payload.get("realm_access", {}).get("roles", [])

    if not user_id or not organization_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "schema_name": schema_name,
        "roles": roles,
    }


def require_permission_any(required_permissions: list[str]):
    def dependency(user=Depends(get_current_user)):
        user_permissions = get_permissions_for_roles(user["roles"])

        if not any(p in user_permissions for p in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return user

    return dependency
