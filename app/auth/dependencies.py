from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.auth import decode_jwt

security = HTTPBearer()


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
