from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QFrame, QMessageBox, QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal, Qt

from app.core.usecases.user import AuthenticateUserInteractor, CreateUserInteractor
from app.database.exceptions import DuplicateUsernameError, InvalidCredentialsError
from app.database.transaction_manager import TransactionManager
from app.database.user_repository import Language, User, UserRepository
from app.ui.locale import current_language, tr


class AuthWindow(QWidget):
    logged_in = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        repo = UserRepository()
        self._register = CreateUserInteractor(repo, TransactionManager(...))
        self._login = AuthenticateUserInteractor(repo, TransactionManager(...))
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        h_box = QHBoxLayout()

        card = QFrame()
        card.setObjectName("card")

        card.setMinimumWidth(320)
        card.setMaximumWidth(400)

        card.setMaximumHeight(500)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        self.title = QLabel("Stego")
        self.title.setObjectName("mainTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.form_heading = QLabel()
        self.form_heading.setObjectName("formHeading")
        self.form_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stack = QStackedWidget()
        self.login_page = self._login_form()
        self.register_page = self._register_form()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)

        self.stack.currentChanged.connect(self._update_heading)

        layout.addWidget(self.title)
        layout.addWidget(self.form_heading)
        layout.addWidget(self.stack)

        h_box.addStretch(1)
        h_box.addWidget(card)
        h_box.addStretch(1)

        outer.addStretch(1)
        outer.addLayout(h_box)
        outer.addStretch(1)

        self.retranslate()
        self._update_heading(0)

    def _login_form(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        self.login_user = QLineEdit()
        self.login_user.setFixedHeight(38)

        self.login_pass = QLineEdit()
        self.login_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_pass.setFixedHeight(38)
        self.login_pass.returnPressed.connect(self._do_login)

        self.login_btn = QPushButton()
        self.login_btn.setObjectName("actionBtn")
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self._do_login)

        self.to_register_btn = QPushButton()
        self.to_register_btn.setObjectName("switchBtn")
        self.to_register_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        lay.addWidget(self.login_user)
        lay.addWidget(self.login_pass)
        lay.addSpacing(6)
        lay.addWidget(self.login_btn)
        lay.addWidget(self.to_register_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        lay.addStretch()
        return w

    def _register_form(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        self.reg_user = QLineEdit()
        self.reg_user.setFixedHeight(38)

        self.reg_pass = QLineEdit()
        self.reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_pass.setFixedHeight(38)

        self.reg_pass2 = QLineEdit()
        self.reg_pass2.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_pass2.setFixedHeight(38)
        self.reg_pass2.returnPressed.connect(self._do_register)

        self.register_btn = QPushButton()
        self.register_btn.setObjectName("actionBtn")
        self.register_btn.setFixedHeight(40)
        self.register_btn.clicked.connect(self._do_register)

        self.to_login_btn = QPushButton()
        self.to_login_btn.setObjectName("switchBtn")
        self.to_login_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        lay.addWidget(self.reg_user)
        lay.addWidget(self.reg_pass)
        lay.addWidget(self.reg_pass2)
        lay.addSpacing(6)
        lay.addWidget(self.register_btn)
        lay.addWidget(self.to_login_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        lay.addStretch()
        return w

    def _update_heading(self, index):
        if index == 0:
            self.form_heading.setText(tr("Sign in"))
        else:
            self.form_heading.setText(tr("Register"))

    def retranslate(self):
        self.login_user.setPlaceholderText(tr("Username"))
        self.login_pass.setPlaceholderText(tr("Password"))
        self.login_btn.setText(tr("Sign in button"))
        self.to_register_btn.setText(tr("Register"))

        self.reg_user.setPlaceholderText(tr("Username"))
        self.reg_pass.setPlaceholderText(tr("Password"))
        self.reg_pass2.setPlaceholderText(tr("Repeat password"))
        self.register_btn.setText(tr("Create account"))
        self.to_login_btn.setText(tr("Back to sign in"))

    def _do_login(self):
        user = self.login_user.text().strip()
        pwd = self.login_pass.text()
        if not user or not pwd:
            QMessageBox.warning(self, tr("Sign in"), tr("Fill in username and password."))
            return
        try:
            account: User = self._login.execute(user, pwd)
            self.logged_in.emit(account)
        except InvalidCredentialsError:
            QMessageBox.warning(self, tr("Sign in"), tr("Invalid username or password."))
        except Exception as e:
            QMessageBox.critical(self, tr("Error"), str(e))

    def _do_register(self):
        user = self.reg_user.text().strip()
        pwd = self.reg_pass.text()
        pwd2 = self.reg_pass2.text()
        if not user or not pwd:
            QMessageBox.warning(self, tr("Register"), tr("Fill in all fields."))
            return
        if pwd != pwd2:
            QMessageBox.warning(self, tr("Register"), tr("Passwords do not match."))
            return
        try:
            self._register.execute(user, pwd, current_language())
            QMessageBox.information(self, tr("Register"), tr("Account created. Please sign in."))
            self.login_user.setText(user)
            self.login_pass.clear()
            self.stack.setCurrentIndex(0)
        except DuplicateUsernameError:
            QMessageBox.warning(self, tr("Register"), tr("This username is already taken."))
        except Exception as e:
            QMessageBox.critical(self, tr("Error"), str(e))
