import yaml
from pathlib import Path

PERMISSIONS_FILE = Path(__file__).parent / "permissions.yml"

with open(PERMISSIONS_FILE, "r") as f:
    _permissions = yaml.safe_load(f)["roles"]


def get_permissions_for_roles(roles: list[str]) -> set[str]:
    permissions = set()
    for role in roles:
        permissions.update(_permissions.get(role, []))
    return permissions
