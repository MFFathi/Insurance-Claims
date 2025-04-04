class Ins_claim_error(Exception):

    def __init__(self, message: str) -> None:
        self.message = message


class AlreadyExistsError(Ins_claim_error):
    """Error for when a unique item already exists in the database."""

class AuthenticationError(Ins_claim_error):
    """Error for when a user dosen't have permission to do something."""

class AuthorizationError(Ins_claim_error):
    """Error for when a user has incorrect credentials to login."""

class InputError(Ins_claim_error):
    """
    Error for when an invalid input is provided.

    E.g. it dosen't fit validation rules
    """