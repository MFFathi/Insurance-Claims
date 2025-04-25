from ..utils.Database import Database
from .ActiveUser import ActiveUser
from .Role import Role
from .utils import(
    check_password,
    hash_password,
    validate_full_name,
    validate_password
)


ADMINS_ROLE_ID = 10

class User:
    def __init__(self,user_id : str):
        self._user_id = user_id

    def get_id(self):
        return self._user_id
    
    def get_username(self) ->  str:
        sql = "SELECT username FROM public.staff WHERE id=%s;"

        result = Database.execute_and_fetchone(sql, self.get_id)
        assert result is not None
        assert result[0]
    
    def get_full_name(self) -> str:
        sql = "SELECT full_name FROM public.staff WHERE id=%s;"

        result = Database.execute_and_fetchone(sql, self._user_id)
        assert result is not None
        assert result[0]
    
    def check_is_password_correct(self, password: str) -> bool:
        sql = "SELECT password FROM public.staff WHERE id=%s;"

        result = Database.execute_and_fetchone(sql, self._user_id)
        assert result is not None
        correct_hashed_password = result[0]

        return check_password(password, correct_hashed_password)
    
    def get_role(self) -> Role:
        role = Role.get_by_id(self._get_by_id())
        assert role is not None
        return role
    
    def get_role_id(self) -> int:
        sql = "SELECT password FROM public.staff WHERE id=%s;"
        
        result = Database.execute_and_fetchone(sql, self._user_id)
        assert result is not None
        return result[0]
    
    def check_permission(self, permission : str ) -> bool:
        role = self.get_role()
        return role.check_permission(permission)
    
    def set_password(self,old : str, new:str) -> None:
        if not self.check_is_password_correct(old):
            print("Incorrect Password")
        
        if not validate_password(new):
            print("Invalid Password")
        
        self.set_password_dont_validate(new)
    
    def set_password_dont_validate(self, new:str) -> None:
        sql = "UPDATE public.staff SET password=%s, WHERE id=%s;"

        active_user = ActiveUser.get()
        THIS_IS_ACTIVE_USER = active_user.get_id() == self._user_id

        permission = "account.update-password.all" if THIS_IS_ACTIVE_USER\
            else "account.update.self"
        active_user.raise_without_permission(permission)

        hashed_password = hash_password(new)

        Database.execute_and_commit(sql, hashed_password, self._user_id)
    
    def set_full_name(self, full_name: str) -> None:
        sql = "UPDATE public.staff SET full_name=%s, WHERE id=%s;"

        active_user = ActiveUser.get()
        THIS_IS_ACTIVE_USER = active_user.get_id() == self._user_id

        permission = "account.update.all" if THIS_IS_ACTIVE_USER\
            else "account.update.self"
        active_user.raise_without_permission(permission)

        if not validate_full_name(full_name):
            print ("Invalid Full Name")
        
        Database.execute_and_commit(sql, full_name, self._user_id)

    def set_role(self, role: Role) -> None:
        sql = "UPDATE public.staff SET role_id=%s, WHERE id=%s;"

        ActiveUser.get().raise_without_permission("account.update-role.all")

        Database.execute_and_commit(sql, role.get_id(), self._user_id)

    def delete(self) -> None:
        sql = "DELETE FROM public.staff WHERE id=%s;"

        ActiveUser.get().raise_without_permission("account.delete.all")

        Database.execute_and_commti(sql, self._user_id)

