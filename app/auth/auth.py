"""
JWT Authentication and Keycloak Integration

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Handles JWT token validation and decoding using Keycloak public keys.
    Provides secure authentication for FastAPI endpoints with caching for JWKS.
"""

import os
import requests
from jose import jwt, JWTError
from fastapi import HTTPException, status

KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_URL = os.getenv("KEYCLOAK_BASE_URL") 
ALGORITHMS = ["RS256"]

JWKS_URL = (
    f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
)

_jwks_cache = None


def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        response = requests.get(JWKS_URL)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def decode_jwt(token: str) -> dict:
    try:
        jwks = get_jwks()

        payload = jwt.decode(
            token,
            jwks,
            algorithms=ALGORITHMS,
            issuer=f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}",
            options={
                "verify_aud": False  # IMPORTANT for Keycloak
            },
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
