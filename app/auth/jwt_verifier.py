from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.auth.jwks_config import JWKSClient, JWKSConfig


class JWTVerifier:
    def __init__(self, config: JWKSConfig, jwks_client: Optional[JWKSClient] = None):
        self._config = config
        self._jwks_client = jwks_client or JWKSClient(config)

    def decode(self, token: str) -> dict:
        try:
            jwks = self._jwks_client.get_jwks()
            return jwt.decode(
                token,
                jwks,
                algorithms=self._config.algorithms,
                issuer=self._config.issuer,
                options={
                    "verify_aud": False,  # Keycloak tokens may omit audience
                },
            )
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(exc)}",
            )
