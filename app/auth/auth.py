from app.auth.jwks_config import default_jwks_config
from app.auth.jwt_verifier import JWTVerifier

_jwt_verifier = JWTVerifier(default_jwks_config())


def decode_jwt(token: str) -> dict:
    return _jwt_verifier.decode(token)
