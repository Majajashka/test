from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QFrame, QLabel,
)

from app.database.user_repository import Language, User
from app.ui.auth import AuthWindow
from app.ui.locale import install_language, tr
from app.ui.pages import (
    TextToImagePage, ImageToTextPage,
    StegoEncodePage, StegoDecodePage, SettingsPage, HistoryPage,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._user = None
        self.setWindowTitle("Stego")
        self.setMinimumSize(720, 520)
        self.resize(800, 560)
        self._build()

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        self.stack = QStackedWidget()

        self.auth = AuthWindow()
        self.auth.logged_in.connect(self._enter_app)

        self.app_widget = self._build_app()
        self.stack.addWidget(self.auth)
        self.stack.addWidget(self.app_widget)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        install_language(Language.EN)
        self.auth.retranslate()

    def _build_app(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(0, 12, 0, 12)
        side_lay.setSpacing(0)

        self.pages = QStackedWidget()
        self.page_text_encode = TextToImagePage()
        self.page_text_decode = ImageToTextPage()
        self.page_stego_encode = StegoEncodePage()
        self.page_stego_decode = StegoDecodePage()
        self.page_history = HistoryPage()
        self.page_settings = SettingsPage()
        self.page_settings.language_changed.connect(self._apply_language)

        self.pages.addWidget(self.page_text_encode)
        self.pages.addWidget(self.page_text_decode)
        self.pages.addWidget(self.page_stego_encode)
        self.pages.addWidget(self.page_stego_decode)
        self.pages.addWidget(self.page_history)
        self.pages.addWidget(self.page_settings)

        self._nav_sources = [
            "Text to Image",
            "Image to Text",
            "Steganography → Encode",
            "Steganography → Decode",
            "History",
            "Settings",
        ]
        self.nav_buttons = []
        for index, source in enumerate(self._nav_sources):
            btn = QPushButton()
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self._go(i))
            side_lay.addWidget(btn)
            self.nav_buttons.append((btn, source))

        side_lay.addStretch()

        self.logout_btn = QPushButton()
        self.logout_btn.clicked.connect(self._logout)
        side_lay.addWidget(self.logout_btn)

        self.user_info = QLabel()
        self.user_info.setObjectName("sidebarUserInfo")
        self.user_info.setContentsMargins(16, 12, 16, 12)
        side_lay.addWidget(self.user_info)

        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)

        self._go(0)
        return widget

    def _go(self, index):
        for i, (btn, _) in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.pages.setCurrentIndex(index)

    def _apply_language(self, lang: Language | None = None):
        if lang is None and self._user:
            lang = self._user.preferred_lang_code
        if lang is not None:
            install_language(lang)
        self.auth.retranslate()
        for btn, source in self.nav_buttons:
            btn.setText(tr(source))
        self.logout_btn.setText(tr("Log out"))
        self.page_text_encode.retranslate()
        self.page_text_decode.retranslate()
        self.page_stego_encode.retranslate()
        self.page_stego_decode.retranslate()
        self.page_settings.retranslate()

    def _enter_app(self, user: User):
        self._user = user
        self.user_info.setText(f"<span>User:</span> <strong>{user.username}</strong>")
        self.page_settings.set_user(user)
        self.page_text_decode.set_user(user)
        self.page_text_encode.set_user(user)
        self.page_stego_decode.set_user(user)
        self.page_stego_encode.set_user(user)
        self.page_history.set_user(user)
        self._apply_language(user.preferred_lang_code)
        self.stack.setCurrentIndex(1)
        self._go(0)

    def _logout(self):
        self._user = None
        self.auth.login_pass.clear()
        install_language(Language.EN)
        self.auth.retranslate()
        self.stack.setCurrentIndex(0)
