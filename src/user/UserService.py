from typing import TYPE_CHECKING

from psycopg2.errors import UniqueViolation

from ..utils.Database import Database
from .ActiveUser import ActiveUser
from .Role import Role
from .User import User
from .utils import (
    hash_password,
    validate_full_name,
    validate_password,
    validate_username,
)

class UserService:
    _active_user: User | None = None

    @staticmethod
    def init():
        print("Initializing UserService...")

        admin_user = UserService.get_by_username("admin", dont_auth=True)
        if admin_user is None:
            UserService.create("admin", "admin", "Administrator", role_id=99)

        ActiveUser.clear()  # Makes sure the active user is None
        Role.load_roles()

    @staticmethod
    def create(username: str,
               password: str,
               full_name: str,
               role_id: int = 0) -> User:
        
        sql = """
        INSERT INTO public.staff (username, password, full_name, role_id)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """

        # Creating an admin account is handle immediately at initialisation
        # so does not require permission checks and validation.
        if username != "admin":
            UserService._validate_create_user(username, password, full_name)
            ActiveUser.get().raise_without_permission("account.create")

        hashed_password = hash_password(password)

        try:
            cursor = Database.execute(
                sql, username, hashed_password, full_name, role_id)
        except UniqueViolation:
            print(f"User {username} already exists")

        Database.commit()
        result = cursor.fetchone()
        assert result is not None
        user = User(result[0])

        return user

    @staticmethod
    def get_by_username(username: str, dont_auth: bool = False) -> User | None:
        if not dont_auth:
            IS_ACTIVE_USER = ActiveUser.get().get_username() == username
            permission = "account.view.self" if IS_ACTIVE_USER\
                else "account.view.all"
            ActiveUser.get().raise_without_permission(permission)

        sql = "SELECT id FROM public.staff WHERE username=%s"
        result = Database.execute_and_fetchone(sql, username)

        if result is None:
            return None

        id = result[0]
        return User(id)

    @staticmethod
    def get_by_id(id: str, dont_auth: bool = False) -> User | None:
        if not dont_auth:
            IS_ACTIVE_USER = ActiveUser.get().get_id() == id
            permission = "account.view.self" if IS_ACTIVE_USER\
                else "account.view.all"
            ActiveUser.get().raise_without_permission(permission)

        sql = "SELECT id FROM public.staff WHERE id=%s;"
        result = Database.execute_and_fetchone(sql, id)

        if result is None:
            return None

        id = result[0]
        return User(id)

    @staticmethod
    def get_all(dont_auth: bool = False) -> list[User]:
        if not dont_auth:
            ActiveUser.get().raise_without_permission("account.view.all")

        sql = "SELECT id FROM public.staff;"
        result = Database.execute_and_fetchall(sql)

        return [User(record[0]) for record in result]

    @staticmethod
    def login(username: str, password: str) -> User:
        user = UserService.get_by_username(username, dont_auth=True)

        if (user is None) or (not user.check_is_password_correct(password)):
            print("Username or password incorrect")

        ActiveUser.set(user)
        return user

    @staticmethod
    def logout() -> None:
        ActiveUser.clear()

    @staticmethod
    def _validate_create_user(username: str, password: str, full_name: str):
        if not validate_username(username):
            print(
                "Invalid username. Must be between 3 and 15 characters, start\
                with a letter, and only contain letters, numbers, and hyphens")

        if not validate_password(password):
            print(
                "Invalid password. Must be between 8 and 100 characters,\
                contain at least one uppercase letter, one lowercase letter,\
                one number, and one special character")

        if not validate_full_name(full_name):
            print("Invalid full name. Must be between 2 and 50 characters, start\
                and end with a letter, and only contain letters and spaces")