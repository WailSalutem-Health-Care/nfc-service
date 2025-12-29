from pathlib import Path
from typing import Union

import yaml


class PermissionsStore:
    def __init__(self, permissions_file: Union[Path, str]):
        self._permissions_file = Path(permissions_file)
        with open(self._permissions_file, "r") as f:
            self._permissions = yaml.safe_load(f)["roles"]

    def get_permissions_for_roles(self, roles: list[str]) -> set[str]:
        permissions = set()
        for role in roles:
            permissions.update(self._permissions.get(role, []))
        return permissions
