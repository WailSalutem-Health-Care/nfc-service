"""
Permission Management and Role-Based Access Control

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Handles role-based access control (RBAC) by loading permissions from YAML configuration.
    Maps user roles to their corresponding permissions.
"""

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
