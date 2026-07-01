from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QTranslator
from PyQt6.QtWidgets import QApplication

from app.database.user_repository import Language

CONTEXT = "Stego"
TRANSLATIONS_DIR = Path(__file__).parent / "translations"
_translator = QTranslator()
_current = Language.RU


def tr(text: str) -> str:
    return QCoreApplication.translate(CONTEXT, text)


def current_language() -> Language:
    return _current


def install_language(lang: Language) -> None:
    global _current
    app = QApplication.instance()
    if app is None:
        _current = lang
        return

    app.removeTranslator(_translator)
    _current = lang

    if lang == Language.EN:
        return

    if _translator.load(f"stego_{lang.value}", str(TRANSLATIONS_DIR)):
        app.installTranslator(_translator)
