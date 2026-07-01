from pathlib import Path

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton,
    QFormLayout, QComboBox, QMessageBox, QLineEdit, QHBoxLayout, QTableWidgetItem, QHeaderView,
    QTableWidget, QTabWidget, QMenu, QApplication, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt

from app.database.connection import get_connection
from app.database.image_repository import ImageRepository, Image
from app.database.operation_repository import OperationRepository, Operation
from app.database.transaction_manager import TransactionManager
from app.database.user_repository import Language, User, UserRepository
from app.ui.locale import tr
from app.ui.services import rgb_pack_interactor, rgb_unpack_interactor, lsb_pack_interactor, \
    lsb_unpack_interactor
from app.ui.widgets import PathRow, PackSettings, WorkerMixin


class TextToImagePage(QWidget, WorkerMixin):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(10)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")

        self.lbl_text = QLabel()
        self.lbl_text.setObjectName("fieldLabel")

        self.text = QPlainTextEdit()
        self.text.setMinimumHeight(140)

        self.lbl_output = QLabel()
        self.lbl_output.setObjectName("fieldLabel")

        self.output = PathRow("Save PNG to", save_dialog=True, file_filter="PNG (*.png)")
        self.settings = PackSettings()

        self.btn = QPushButton()
        self.btn.setObjectName("actionBtn")
        self.btn.setFixedHeight(40)
        self.btn.clicked.connect(self._run)

        lay.addWidget(self.title)
        lay.addSpacing(10)
        lay.addWidget(self.lbl_text)
        lay.addWidget(self.text)
        lay.addWidget(self.lbl_output)
        lay.addWidget(self.output)

        lay.addSpacing(10)
        lay.addWidget(self.settings)

        lay.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn)
        self.btn.setFixedWidth(160)
        lay.addLayout(btn_layout)
        self.user = None
        self.retranslate()

    def retranslate(self):
        self.title.setText(tr("Text to Image"))
        self.lbl_text.setText(tr("Text:"))
        self.text.setPlaceholderText(tr("Enter text..."))
        self.lbl_output.setText(tr("Output file:"))
        self.output.retranslate()
        self.settings.retranslate()
        self.btn.setText(tr("Save"))

    def _run(self):
        text = self.text.toPlainText()
        path = self.output.text()

        if not text:
            QMessageBox.warning(self, tr("Validation"), tr("Enter text."))
            return
        if not path:
            QMessageBox.warning(self, tr("Validation"), tr("Specify output path."))
            return

        self.btn.setEnabled(False)
        opts = self.settings.values()

        self._current_thread = self.run_async(
            func=rgb_pack_interactor().execute,
            on_success=lambda result, duration: self._on_success(path, duration),
            on_error=self._on_error,
            user_id=self.user.id,
            text=text,
            path_to_save=Path(path),
            **opts
        )

    def _on_success(self, path, duration):
        self.btn.setEnabled(True)
        message = tr("Saved: %1 (%2 ms)")
        message = message.replace("%1", path).replace("%2", str(int(duration)))
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)
            operation_repo.log_operation(
                self.user.id, "EMBED", "SUCCESS", duration_ms=duration
            )
            tm.commit()
        QMessageBox.information(self, tr("Success"), message)

    def _on_error(self, error_msg, duration):
        self.btn.setEnabled(True)
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)
            operation_repo.log_operation(
                self.user.id, "EMBED", "FAILED", duration_ms=duration
            )
            tm.commit()
        QMessageBox.critical(self, tr("Error"), error_msg)

    def set_user(self, user: User):
        self.user = user


class ImageToTextPage(QWidget, WorkerMixin):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(10)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")

        self.lbl_image = QLabel()
        self.lbl_image.setObjectName("fieldLabel")
        self.image = PathRow("Path to image", file_filter="PNG (*.png)")

        self.lbl_password = QLabel()
        self.lbl_password.setObjectName("fieldLabel")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(38)

        self.lbl_result = QLabel()
        self.lbl_result.setObjectName("fieldLabel")
        self.result = QPlainTextEdit()
        self.result.setReadOnly(True)
        self.result.setMinimumHeight(140)

        self.btn = QPushButton()
        self.btn.setObjectName("actionBtn")
        self.btn.setFixedHeight(40)
        self.btn.setFixedWidth(160)
        self.btn.clicked.connect(self._run)

        lay.addWidget(self.title)
        lay.addSpacing(10)
        lay.addWidget(self.lbl_image)
        lay.addWidget(self.image)
        lay.addWidget(self.lbl_password)
        lay.addWidget(self.password)

        lay.addSpacing(10)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn)
        lay.addLayout(btn_layout)

        lay.addWidget(self.lbl_result)
        lay.addWidget(self.result)
        lay.addStretch()
        self.user = None
        self.retranslate()

    def retranslate(self):
        self.title.setText(tr("Image to Text"))
        self.lbl_image.setText(tr("Image:"))
        self.image.retranslate()
        self.lbl_password.setText(tr("Password:"))
        self.password.setPlaceholderText(tr("Password (if required)"))
        self.lbl_result.setText(tr("Result:"))
        self.result.setPlaceholderText(tr("Extracted text..."))
        self.btn.setText(tr("Extract"))

    def _run(self):
        path = self.image.text()
        if not path:
            QMessageBox.warning(self, tr("Validation"), tr("Specify image path."))
            return
        if not Path(path).is_file():
            QMessageBox.warning(self, tr("Validation"), tr("File not found."))
            return

        pwd = self.password.text() or None
        interactor = rgb_unpack_interactor()

        def job():
            return interactor.execute(Path(path), password=pwd)

        self.run_async(
            job,
            on_success=self._on_success,
            on_error=self._on_error
        )

    def _on_success(self, result, duration):
        self.btn.setEnabled(True)
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)
            operation_repo.log_operation(
                self.user.id, "EXTRACT", "SUCCESS", duration_ms=duration
            )
            tm.commit()
        self.result.setPlainText(str(result))

    def _on_error(self, error_msg, duration):
        print(error_msg)
        self.btn.setEnabled(True)
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)
            operation_repo.log_operation(
                self.user.id, "EXTRACT", "FAILED", error_message=error_msg, duration_ms=duration
            )
            tm.commit()
        QMessageBox.critical(self, tr("Error"), error_msg)

    def set_user(self, user: User):
        self.user = user


class StegoEncodePage(QWidget, WorkerMixin):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(10)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")

        self.lbl_text = QLabel()
        self.lbl_text.setObjectName("fieldLabel")
        self.text = QPlainTextEdit()
        self.text.setMinimumHeight(120)

        self.lbl_cover = QLabel()
        self.lbl_cover.setObjectName("fieldLabel")
        self.cover = PathRow("Cover image (embed into)",
                             file_filter="Images (*.png *.jpg *.jpeg *.bmp)")

        self.lbl_output = QLabel()
        self.lbl_output.setObjectName("fieldLabel")
        self.output = PathRow("Save result to", save_dialog=True, file_filter="PNG (*.png)")

        self.settings = PackSettings()

        self.btn = QPushButton()
        self.btn.setObjectName("actionBtn")
        self.btn.setFixedHeight(40)
        self.btn.setFixedWidth(160)
        self.btn.clicked.connect(self._run)

        lay.addWidget(self.title)
        lay.addSpacing(10)
        lay.addWidget(self.lbl_text)
        lay.addWidget(self.text)
        lay.addWidget(self.lbl_cover)
        lay.addWidget(self.cover)
        lay.addWidget(self.lbl_output)
        lay.addWidget(self.output)

        lay.addSpacing(10)
        lay.addWidget(self.settings)
        lay.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn)
        lay.addLayout(btn_layout)
        self.user = None
        self.retranslate()

    def retranslate(self):
        self.title.setText(tr("Steganography → Encode"))
        self.lbl_text.setText(tr("Text:"))
        self.text.setPlaceholderText(tr("Enter text..."))
        self.lbl_cover.setText(tr("Cover image:"))
        self.cover.retranslate()
        self.lbl_output.setText(tr("Output:"))
        self.output.retranslate()
        self.settings.retranslate()
        self.btn.setText(tr("Embed"))

    def _run(self):
        text = self.text.toPlainText()
        cover = self.cover.text()
        out = self.output.text()

        if not text:
            QMessageBox.warning(self, tr("Validation"), tr("Enter text."))
            return
        if not cover or not Path(cover).is_file():
            QMessageBox.warning(self, tr("Validation"), tr("Specify a valid cover image."))
            return
        if not out:
            QMessageBox.warning(self, tr("Validation"), tr("Specify output path."))
            return

        opts = self.settings.values()

        self.btn.setEnabled(False)

        def job():
            interactor = lsb_pack_interactor()
            interactor.execute(
                text=text,
                source_path=Path(cover),
                path_to_save=Path(out),
                user_id=self.user.id,
                **opts,
            )
            return tr("Saved: %1").replace("%1", out)

        self.run_async(
            func=job,
            on_success=self._on_success,
            on_error=self._on_error
        )

    def _on_success(self, message, duration):
        self.btn.setEnabled(True)
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)
            operation_repo.log_operation(
                self.user.id, "EMBED", "SUCCESS", duration_ms=duration
            )
            tm.commit()
        QMessageBox.information(self, tr("Done"), message)

    def _on_error(self, error_msg, duration):
        self.btn.setEnabled(True)
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)

            operation_repo.log_operation(
                self.user.id, "EMBED", "FAILED", error_message=error_msg, duration_ms=duration
            )
            tm.commit()
        QMessageBox.critical(self, tr("Error"), error_msg)

    def set_user(self, user: User):
        self.user = user


class StegoDecodePage(QWidget, WorkerMixin):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(10)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")

        self.lbl_image = QLabel()
        self.lbl_image.setObjectName("fieldLabel")
        self.image = PathRow("Path to image", file_filter="Images (*.png *.jpg *.jpeg *.bmp)")

        self.lbl_password = QLabel()
        self.lbl_password.setObjectName("fieldLabel")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(38)

        self.lbl_result = QLabel()
        self.lbl_result.setObjectName("fieldLabel")
        self.result = QPlainTextEdit()
        self.result.setReadOnly(True)
        self.result.setMinimumHeight(140)

        self.btn = QPushButton()
        self.btn.setObjectName("actionBtn")
        self.btn.setFixedHeight(40)
        self.btn.setFixedWidth(160)
        self.btn.clicked.connect(self._run)

        lay.addWidget(self.title)
        lay.addSpacing(10)
        lay.addWidget(self.lbl_image)
        lay.addWidget(self.image)
        lay.addWidget(self.lbl_password)
        lay.addWidget(self.password)

        lay.addSpacing(10)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn)
        lay.addLayout(btn_layout)

        lay.addWidget(self.lbl_result)
        lay.addWidget(self.result)
        lay.addStretch()
        self.user = None
        self.retranslate()

    def retranslate(self):
        self.title.setText(tr("Steganography → Decode"))
        self.lbl_image.setText(tr("Image:"))
        self.image.retranslate()
        self.lbl_password.setText(tr("Password:"))
        self.password.setPlaceholderText(tr("Password (if required)"))
        self.lbl_result.setText(tr("Result:"))
        self.result.setPlaceholderText(tr("Extracted text..."))
        self.btn.setText(tr("Extract"))

    def _run(self):
        path = self.image.text()
        if not path:
            QMessageBox.warning(self, tr("Validation"), tr("Specify image path."))
            return
        if not Path(path).is_file():
            QMessageBox.warning(self, tr("Validation"), tr("File not found."))
            return

        pwd = self.password.text() or None
        self.btn.setEnabled(False)

        def job():
            interactor = lsb_unpack_interactor()
            return interactor.execute(Path(path), password=pwd)

        self.run_async(
            func=job,
            on_success=self._on_success,
            on_error=self._on_error
        )

    def _on_success(self, text, duration):
        self.btn.setEnabled(True)
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)
            operation_repo.log_operation(
                self.user.id, "EXTRACT", "SUCCESS", duration_ms=duration
            )
            tm.commit()
        self.result.setPlainText(text)

    def _on_error(self, error_msg, duration):
        self.btn.setEnabled(True)
        conn = get_connection()
        with TransactionManager(conn) as tm:
            operation_repo = OperationRepository(conn)

            operation_repo.log_operation(
                self.user.id, "EMBED", "FAILED", error_message=error_msg, duration_ms=duration
            )
            tm.commit()
        QMessageBox.critical(self, tr("Error"), error_msg)

    def set_user(self, user: User):
        self.user = user


class SettingsPage(QWidget):
    language_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._user: User | None = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(20)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")

        form = QFormLayout()
        form.setSpacing(14)

        self.lbl_user = QLabel()
        self.user_label = QLabel("—")
        self.user_label.setStyleSheet("font-weight: bold; color: #ffffff;")

        self.lbl_lang = QLabel()
        self.lang = QComboBox()
        self.lang.setFixedHeight(36)
        self.lang.addItem("", Language.RU)
        self.lang.addItem("", Language.EN)
        self.lang.addItem("", Language.KA)

        form.addRow(self.lbl_user, self.user_label)
        form.addRow(self.lbl_lang, self.lang)

        self.btn = QPushButton()
        self.btn.setObjectName("actionBtn")
        self.btn.setFixedHeight(40)
        self.btn.setFixedWidth(140)
        self.btn.clicked.connect(self._save)

        lay.addWidget(self.title)
        lay.addSpacing(10)
        lay.addLayout(form)
        lay.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn)
        lay.addLayout(btn_layout)
        self.retranslate()

    def retranslate(self):
        self.title.setText(tr("Settings"))
        self.lbl_user.setText(tr("User:"))
        self.lbl_lang.setText(tr("Language:"))
        self.lang.setItemText(0, tr("Russian"))
        self.lang.setItemText(1, tr("English"))
        self.lang.setItemText(2, tr("Georgian"))
        self.btn.setText(tr("Save"))

    def set_user(self, user: User):
        self._user = user
        self.user_label.setText(user.username)
        idx = self.lang.findData(user.preferred_lang_code)
        if idx >= 0:
            self.lang.setCurrentIndex(idx)

    def _save(self):
        if not self._user:
            return
        lang = self.lang.currentData()
        try:
            conn = get_connection()
            with TransactionManager(conn) as tm:
                UserRepository(conn).change_language(self._user.id, lang)
                tm.commit()
            self._user.preferred_lang_code = lang
            self.language_changed.emit()
            QMessageBox.information(self, tr("Settings"), tr("Saved."))
        except Exception as e:
            QMessageBox.critical(self, tr("Error"), str(e))


def make_history_table(column_count: int) -> QTableWidget:
    table = QTableWidget()
    table.setColumnCount(column_count)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
    table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setVisible(False)
    table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    return table


def add_copy_support(table: QTableWidget):
    def copy_selection():
        selected = table.selectedItems()
        if not selected:
            return
        if len(selected) == 1:
            QApplication.clipboard().setText(selected[0].text())
            return
        rows = sorted(set(item.row() for item in selected))
        cols = sorted(set(item.column() for item in selected))
        lines = []
        for r in rows:
            line = []
            for c in cols:
                item = table.item(r, c)
                line.append(item.text() if item else "")
            lines.append("\t".join(line))
        QApplication.clipboard().setText("\n".join(lines))

    def show_context_menu(pos):
        if not table.selectedItems():
            return
        menu = QMenu(table)
        copy_action = QAction(tr("Copy"), table)
        copy_action.triggered.connect(copy_selection)
        menu.addAction(copy_action)
        menu.exec(table.viewport().mapToGlobal(pos))

    table.customContextMenuRequested.connect(show_context_menu)

    copy_action = QAction(table)
    copy_action.setShortcut("Ctrl+C")
    copy_action.triggered.connect(copy_selection)
    table.addAction(copy_action)


def set_item(table: QTableWidget, row: int, col: int, text: str):
    item = QTableWidgetItem(text)
    item.setToolTip(text)
    table.setItem(row, col, item)


class HistoryPage(QWidget, WorkerMixin):
    def __init__(self):
        super().__init__()
        self.user = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(10)

        header = QHBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        header.addWidget(self.title)
        header.addStretch()

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedWidth(120)
        self.btn_refresh.clicked.connect(self.reload)
        header.addWidget(self.btn_refresh)

        lay.addLayout(header)
        lay.addSpacing(10)

        self.tabs = QTabWidget()

        self.operations_table = make_history_table(5)
        add_copy_support(self.operations_table)

        self.images_table = make_history_table(8)
        add_copy_support(self.images_table)

        self.tabs.addTab(self.operations_table, "")
        self.tabs.addTab(self.images_table, "")

        lay.addWidget(self.tabs)

        self.retranslate()
        self._configure_column_widths()

    def _configure_column_widths(self):
        op_widths = [140, 90, 90, 100, 250]
        for i, w in enumerate(op_widths):
            self.operations_table.setColumnWidth(i, w)

        img_widths = [140, 160, 280, 70, 90, 90, 60, 140]
        for i, w in enumerate(img_widths):
            self.images_table.setColumnWidth(i, w)

    def retranslate(self):
        self.title.setText(tr("History"))
        self.btn_refresh.setText(tr("Refresh"))
        self.tabs.setTabText(0, tr("Operations"))
        self.tabs.setTabText(1, tr("Images"))

        self.operations_table.setHorizontalHeaderLabels([
            tr("Date"), tr("Type"), tr("Status"), tr("Duration (ms)"), tr("Error"),
        ])
        self.images_table.setHorizontalHeaderLabels([
            tr("Date"), tr("File"), tr("Path"), tr("Format"), tr("Channels"),
            tr("Size"), tr("Stego"), tr("Hash"),
        ])

    def set_user(self, user):
        self.user = user
        self.operations_table.setRowCount(0)
        self.images_table.setRowCount(0)

    def showEvent(self, event):
        super().showEvent(event)
        if self.user:
            self.reload()

    def reload(self):
        if not self.user:
            return
        self.btn_refresh.setEnabled(False)
        self.run_async(
            func=self._fetch_history,
            on_success=self._on_loaded,
            on_error=self._on_load_error,
        )

    def _fetch_history(self):
        conn = get_connection()
        try:
            operations = OperationRepository(conn).list_by_user(self.user.id)
            images = ImageRepository(conn).list_by_owner(self.user.id)
            return operations, images
        except Exception as e:
            print(e)
            return None, None

    def _on_loaded(self, result, duration):
        operations, images = result
        self._fill_operations(operations)
        self._fill_images(images)
        self.btn_refresh.setEnabled(True)

    def _on_load_error(self, error_msg, duration):
        self.btn_refresh.setEnabled(True)
        QMessageBox.critical(self, tr("Error"), error_msg)

    def _fill_operations(self, rows: list[Operation]):
        self.operations_table.setRowCount(len(rows))
        for i, operation in enumerate(rows):
            status_item = QTableWidgetItem(operation.status)
            status_item.setToolTip(operation.status)
            if operation.status == "FAILED":
                status_item.setForeground(Qt.GlobalColor.red)
            else:
                status_item.setForeground(Qt.GlobalColor.darkGreen)

            set_item(self.operations_table, i, 0, operation.created_at)
            set_item(self.operations_table, i, 1, operation.operation_type)
            self.operations_table.setItem(i, 2, status_item)
            set_item(
                self.operations_table, i, 3,
                str(round(operation.duration_ms, 1)) if operation.duration_ms is not None else "—"
            )
            set_item(self.operations_table, i, 4, operation.error_message or "—")

    def _fill_images(self, rows):
        self.images_table.setRowCount(len(rows))
        for i, img in enumerate(rows):
            name = Path(img.file_path).name
            size = self._format_size(img.file_size_bytes)
            stego = tr("Yes") if img.is_stego else tr("No")
            full_hash = img.sha256_hash or ""

            set_item(self.images_table, i, 0, img.created_at)
            set_item(self.images_table, i, 1, name)
            set_item(self.images_table, i, 2, img.file_path)
            set_item(self.images_table, i, 3, img.image_format)
            set_item(self.images_table, i, 4, img.channels_mask or "—")
            set_item(self.images_table, i, 5, size)
            set_item(self.images_table, i, 6, stego)
            set_item(self.images_table, i, 7, full_hash)

    @staticmethod
    def _format_size(size_bytes: int | None) -> str:
        if size_bytes is None:
            return "—"
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / 1024 ** 2:.1f} MB"
