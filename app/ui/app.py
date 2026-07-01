import sys

from PyQt6.QtWidgets import QApplication, QStyle

from app.ui.main_window import MainWindow
from app.ui.services import ensure_database
from app.ui.styles import APP_STYLE


def main():
    ensure_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
