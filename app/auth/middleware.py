from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.jwt_verifier import JWTVerifier
from app.auth.permissions_store import PermissionsStore

_security = HTTPBearer()


class AuthorizationMiddleware:
    def __init__(self, jwt_verifier: JWTVerifier, permissions_store: PermissionsStore):
        self._jwt_verifier = jwt_verifier
        self._permissions_store = permissions_store

    def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(_security),
    ):
        payload = self._jwt_verifier.decode(credentials.credentials)

        user_id = payload.get("sub")
        organization_id = payload.get("organisationId")
        roles = payload.get("realm_access", {}).get("roles", [])

        if not user_id or not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return {
            "user_id": user_id,
            "organization_id": organization_id,
            "roles": roles,
        }

    def require_permission_any(self, required_permissions: list[str]):
        def dependency(user=Depends(self.get_current_user)):
            user_permissions = self._permissions_store.get_permissions_for_roles(
                user["roles"]
            )

            if not any(p in user_permissions for p in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return user

        return dependency
