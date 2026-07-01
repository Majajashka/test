from app.database.transaction_manager import TransactionManager
from app.database.user_repository import UserRepository, User, Language


class CreateUserInteractor:

    def __init__(self, user_repo: UserRepository, transaction_manager: TransactionManager):
        self.user_repo = user_repo
        self.transaction_manager = transaction_manager

    def execute(
            self,
            username: str,
            password: str,
            preferred_lang_code: Language = Language.KA
    ) -> int:
        user_id = self.user_repo.create_user(username, password, preferred_lang_code)
        # self.transaction_manager.commit()
        return user_id


class AuthenticateUserInteractor:

    def __init__(self, user_repo: UserRepository, transaction_manager: TransactionManager):
        self.user_repo = user_repo
        self.transaction_manager = transaction_manager

    def execute(self, username: str, password: str) -> User:
        return self.user_repo.authenticate(username, password)
