from pathlib import Path

from app.auth.jwks_config import default_jwks_config
from app.auth.jwt_verifier import JWTVerifier
from app.auth.middleware import AuthorizationMiddleware
from app.auth.permissions_store import PermissionsStore

_permissions_file = Path(__file__).parent / "permissions.yml"

_jwks_config = default_jwks_config()
_jwt_verifier = JWTVerifier(_jwks_config)
_permissions_store = PermissionsStore(_permissions_file)
_auth_middleware = AuthorizationMiddleware(_jwt_verifier, _permissions_store)

get_current_user = _auth_middleware.get_current_user
require_permission_any = _auth_middleware.require_permission_any
