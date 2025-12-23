from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.auth import decode_jwt

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_jwt(token)

    user_id = payload.get("sub")
    organization_id = payload.get("organisationId")
    roles = payload.get("realm_access", {}).get("roles", [])

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID missing")

    if not organization_id:
        raise HTTPException(status_code=401, detail="Organization ID missing")

    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "roles": roles,
    }


def require_role(required_roles: list[str]):
    def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        token = credentials.credentials
        payload = decode_jwt(token)

        realm_roles = payload.get("realm_access", {}).get("roles", [])

        if not any(role in realm_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return {
            "user_id": payload.get("sub"),
            "organization_id": payload.get("organisationId"),
            "roles": realm_roles,
        }

    return dependency
