from pathlib import Path

from app.auth.permissions_store import PermissionsStore

PERMISSIONS_FILE = Path(__file__).parent / "permissions.yml"
_permissions_store = PermissionsStore(PERMISSIONS_FILE)


def get_permissions_for_roles(roles: list[str]) -> set[str]:
    return _permissions_store.get_permissions_for_roles(roles)
