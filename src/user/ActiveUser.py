from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .User import User

class ActiveUser:
    
    _active_user : "User | None"

    @staticmethod
    def get() -> "User":
        if ActiveUser._active_user is None:
            print("No User")
        return ActiveUser._active_user
    
    @staticmethod
    def clear():
        ActiveUser._active_user = None 

    @staticmethod
    def set(user : "User") -> None:
        ActiveUser._active_user = user


