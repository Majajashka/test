class DatabaseError(Exception):
    pass


class RecordNotFoundError(DatabaseError):
    pass


class DuplicateUsernameError(DatabaseError):
    pass


class InvalidCredentialsError(DatabaseError):
    pass
