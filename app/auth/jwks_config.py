import os
import requests
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class JWKSConfig:
    keycloak_url: str
    realm: str
    algorithms: list[str]

    @property
    def jwks_url(self) -> str:
        return (
            f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/certs"
        )

    @property
    def issuer(self) -> str:
        return f"{self.keycloak_url}/realms/{self.realm}"


class JWKSClient:
    def __init__(self, config: JWKSConfig):
        self._config = config
        self._jwks_cache = None
        self._lock = Lock()

    def get_jwks(self) -> dict:
        if self._jwks_cache is not None:
            return self._jwks_cache

        with self._lock:
            if self._jwks_cache is None:
                response = requests.get(self._config.jwks_url)
                response.raise_for_status()
                self._jwks_cache = response.json()

        return self._jwks_cache


def default_jwks_config() -> JWKSConfig:
    return JWKSConfig(
        keycloak_url=os.getenv("KEYCLOAK_URL"),
        realm=os.getenv("KEYCLOAK_REALM"),
        algorithms=["RS256"],
    )
