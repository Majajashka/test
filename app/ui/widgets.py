import time

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog,
    QGroupBox, QFormLayout, QComboBox, QLabel, QMessageBox,
)
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt, pyqtSlot

from app.core.image.image import Compression, Encryption
from app.ui.locale import tr


class PathRow(QWidget):
    def __init__(self, placeholder: str, save_dialog=False, file_filter=""):
        super().__init__()
        self._placeholder = placeholder
        self.save_dialog = save_dialog
        self.file_filter = file_filter

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.input = QLineEdit()
        self.input.setFixedHeight(38)

        self.browse_btn = QPushButton("📁")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.setFixedSize(42, 38)  #
        self.browse_btn.clicked.connect(self._browse)

        layout.addWidget(self.input)
        layout.addWidget(self.browse_btn)
        self.retranslate()

    def text(self):
        return self.input.text().strip()

    def set_text(self, value):
        self.input.setText(value)

    def retranslate(self):
        self.input.setPlaceholderText(tr(self._placeholder))

    def _browse(self):
        if self.save_dialog:
            path, _ = QFileDialog.getSaveFileName(self, tr("Save file"), "", self.file_filter)
        else:
            path, _ = QFileDialog.getOpenFileName(self, tr("Open file"), "", self.file_filter)
        if path:
            self.input.setText(path)


class PackSettings(QGroupBox):
    def __init__(self):
        super().__init__()

        form = QFormLayout(self)
        form.setContentsMargins(20, 24, 20, 20)
        form.setVerticalSpacing(14)
        form.setHorizontalSpacing(24)

        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        INPUT_MAX_WIDTH = 280

        self.compression = QComboBox()
        self.compression.setFixedHeight(36)
        self.compression.setMaximumWidth(INPUT_MAX_WIDTH)
        for item in Compression:
            self.compression.addItem(item.name, item)

        self.encryption = QComboBox()
        self.encryption.setFixedHeight(36)
        self.encryption.setMaximumWidth(INPUT_MAX_WIDTH)
        for item in Encryption:
            self.encryption.addItem(item.name, item)

        self.compression_label = QLabel()
        self.compression_label.setObjectName("fieldLabel")

        self.encryption_label = QLabel()
        self.encryption_label.setObjectName("fieldLabel")

        self.password_label = QLabel()
        self.password_label.setObjectName("fieldLabel")

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(36)
        self.password.setMaximumWidth(INPUT_MAX_WIDTH)

        self.password_label.hide()
        self.password.hide()

        self.encryption.currentIndexChanged.connect(self._on_encryption_changed)

        form.addRow(self.compression_label, self.compression)
        form.addRow(self.encryption_label, self.encryption)
        form.addRow(self.password_label, self.password)
        self.retranslate()

    def _on_encryption_changed(self):
        need_password = self.encryption.currentData() != Encryption.NONE
        self.password_label.setVisible(need_password)
        self.password.setVisible(need_password)
        if not need_password:
            self.password.clear()

    def retranslate(self):
        self.setTitle(tr("Packing settings"))
        self.compression_label.setText(tr("Compression:"))
        self.encryption_label.setText(tr("Encryption:"))
        self.password_label.setText(tr("Password:"))

    def values(self):
        enc = self.encryption.currentData()
        password = self.password.text()
        if not password:
            password = None
        return {
            "compression": Compression(self.compression.currentData()),
            "encryption": Encryption(enc),
            "password": password,
        }


class Worker(QObject):
    finished = pyqtSignal(object, float)
    error = pyqtSignal(str, float)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        start = time.perf_counter()
        try:
            result = self.func(*self.args, **self.kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            self.finished.emit(result, duration_ms)
        except Exception as e:
            print(f"[DEBUG] [WorkerThread] Error: {e}")
            duration_ms = (time.perf_counter() - start) * 1000
            self.error.emit(str(e), duration_ms)


class WorkerMixin:
    def run_async(self, func, on_success=None, on_error=None, *args, **kwargs):
        self._thread = QThread()
        self._worker = Worker(func, *args, **kwargs)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)

        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)

        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.error.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        if on_success:
            self._worker.finished.connect(on_success)
        if on_error:
            self._worker.error.connect(on_error)

        self._thread.start()
        return self._thread
