import pytest
from src.user.UserService import UserService
from src.user.User import User
from src.user.Role import Role
from src.user.ActiveUser import ActiveUser
from src.utils.Database import Database
from src.utils.errors import AlreadyExistsError, InputError, AuthorizationError, AuthenticationError
from src.user.utils import validate_username, validate_password, validate_full_name

@pytest.fixture(scope="module", autouse=True)
def setup():
    Database.connect()
    Database.init()
    UserService.init()
    Role._load_role_file("tests/roles/test-default.yml")
    UserService.login("admin", "admin")
    yield
    Database.close()

def test_validations():
    assert validate_username("test123")
    assert not validate_username("Test")
    assert validate_password("myPassword0!")
    assert not validate_password("mypassword")
    assert validate_full_name("Test User")
    assert not validate_full_name("Test User!")

def test_user_creation():
    user = UserService.create("testuser", "Passw0rd!", "Test User")
    assert isinstance(user, User)
    assert user.get_username() == "testuser"

def test_duplicate_user():
    with pytest.raises(AlreadyExistsError):
        UserService.create("testuser", "Passw0rd!", "Another User")

def test_user_authentication():
    user = UserService.login("testuser", "Passw0rd!")
    assert user.get_username() == "testuser"
    assert user.check_is_password_correct("Passw0rd!")

def test_user_role():
    user = UserService.get_by_username("testuser")
    assert user.get_role().get_id() == 0

def test_password_update():
    user = UserService.get_by_username("testuser")
    user.set_password("Passw0rd!", "NewPass1!")
    assert user.check_is_password_correct("NewPass1!")

def test_logout():
    UserService.logout()
    with pytest.raises(AuthenticationError):
        ActiveUser.get()

def test_non_admin_restrictions():
    UserService.login("testuser", "NewPass1!")
    user = UserService.get_by_username("testuser")
    with pytest.raises(AuthorizationError):
        user.set_full_name("New Name")
