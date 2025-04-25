from __future__ import annotations
import os

import yaml


ROLE_DIR_PATH = "src/config/roles"


class Role:
    _roles: dict[int, Role] = {}

    @classmethod
    def load_roles(cls):
        files = os.scandir(ROLE_DIR_PATH)
        sorted_files = sorted(files, key=lambda entry: entry.name)

        for file in sorted_files:
            if file.is_file():
                Role._load_role_file(file.path)
            else:
                print("Skipping directory:", file.name)

    @classmethod
    def _load_role_file(cls, path: str):
        print("Loading role file:", path, end="... ")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        id = data["id"]
        name = data["name"]
        permissions = data["permissions"]
        extends = data.get("extends", None)

        if extends is not None:
            cls._handle_extends(extends, permissions)

        role = Role(id, name, permissions)
        cls._roles[id] = role

        print("Loaded", name)

    @classmethod
    def _handle_extends(cls, extends: list[int] | int, permissions: list[str]):
        if isinstance(extends, list):
            for role_id in extends:
                cls._extend_permissions(role_id, permissions)
        else:
            cls._extend_permissions(extends, permissions)

    @classmethod
    def _extend_permissions(cls, role_id: int, permissions: list[str]) -> None:
        parent_role = cls.get_by_id(role_id)
        if not isinstance(parent_role, Role):
            print("Unrecognised role ID in extends")

        permissions += parent_role.get_all_permissions()

    @classmethod
    def get_by_id(cls, id: int) -> Role | None:
        return cls._roles.get(id, None)

    def __init__(self, id: int, name: str, permissions: list[str]):
        self._role_id = id
        self._name = name
        self._permissions: dict[str, bool] = {}

        self._add_permission_list(permissions)

    def check_permission(self, permission: str) -> bool:
        split_permission = permission.split(".")

        return self._check_split_permission(split_permission)

    def _check_split_permission(self, split_permission: list[str]) -> bool:
        if len(split_permission) == 1:
            HAS_PERMISSION = self._check_exact_permission(split_permission[0])

            if HAS_PERMISSION is not None:
                return HAS_PERMISSION

            return self._check_exact_permission(".*") or False

        permission_str = ".".join(split_permission)
        permission_value = self._check_exact_permission(permission_str)

        if permission_value is None:
            return self._check_split_permission(split_permission[:-1])

        return permission_value

    def get_name(self) -> str:
        return self._name

    def get_id(self) -> int:
        return self._role_id

    def get_all_permissions(self) -> list[str]:
        return list(self._permissions.keys())

    def _check_exact_permission(self, permission: str) -> bool | None:
        perm = self._permissions.get(permission, None)
        print(permission, perm)
        return perm

    def _add_permission_list(self, permissions: list[str]):
        for permission in permissions:
            self._add_permission(permission)

    def _add_permission(self, permission: str):
        if permission.startswith("~"):
            self._permissions[permission[1:]] = False
        else:
            self._permissions[permission] = True