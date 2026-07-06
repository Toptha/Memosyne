"""Home page — document upload, extraction, and preview."""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit,
    QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from modules.extractor import DocumentFactory

UPLOAD_DIR = "data/uploads"


class DropZone(QFrame):
    """Custom drag-and-drop area for file uploads."""

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("drop_zone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        # No icon used
        layout.addSpacing(16)

        text = QLabel("Drop your document here")
        text.setObjectName("drop_text")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)

        hint = QLabel("Supports PDF, TXT, DOCX")
        hint.setObjectName("drop_hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(
                (".pdf", ".txt", ".docx")
            ):
                self.file_dropped.emit(file_path)
                return

    def mousePressEvent(self, event):
        """Allow clicking the zone to open a file dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Document",
                "",
                "Documents (*.pdf *.txt *.docx)"
            )
            if file_path:
                self.file_dropped.emit(file_path)


class HomePage(QWidget):
    """Main application view after login."""

    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._username = ""
        self._email = ""
        self._build_ui()

    def set_user(self, username: str, email: str):
        """Set the logged-in user details."""
        self._username = username
        self._email = email
        self.greeting_label.setText(
            f"Welcome, {username}"
        )

    # ── UI Construction ──────────────────────────────────
    def _build_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header bar ──────────────────────────────────
        header = QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)

        app_title = QLabel("Mnemosyne")
        app_title.setStyleSheet(
            "font-size: 18px; font-weight: 700; "
            "letter-spacing: 1px;"
        )
        header_layout.addWidget(app_title)

        header_layout.addStretch()

        self.greeting_label = QLabel("Welcome")
        self.greeting_label.setObjectName("greeting")
        header_layout.addWidget(self.greeting_label)

        header_layout.addSpacing(16)

        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        logout_btn.clicked.connect(
            self.logout_requested.emit
        )
        header_layout.addWidget(logout_btn)

        main_layout.addWidget(header)

        # ── Content area ────────────────────────────────
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 36, 48, 36)
        content_layout.setSpacing(0)

        # Section title
        section_title = QLabel("SEMANTIC DOCUMENT SEARCH")
        section_title.setObjectName("section_label")
        content_layout.addWidget(section_title)

        content_layout.addSpacing(4)

        section_desc = QLabel(
            "Upload a document to extract and preview its contents"
        )
        section_desc.setStyleSheet(
            "color: #666666; font-size: 13px;"
        )
        content_layout.addWidget(section_desc)

        content_layout.addSpacing(24)

        # ── Upload area (drop zone + button row) ────────
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(
            self._process_file
        )
        content_layout.addWidget(self.drop_zone)

        content_layout.addSpacing(12)

        upload_row = QHBoxLayout()
        upload_row.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        browse_btn = QPushButton("Browse Files")
        browse_btn.setObjectName("upload_btn")
        browse_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        browse_btn.clicked.connect(self._browse_file)
        upload_row.addWidget(browse_btn)

        upload_row.addStretch()

        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("success_label")
        self.status_label.hide()
        upload_row.addWidget(self.status_label)

        content_layout.addLayout(upload_row)

        content_layout.addSpacing(8)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        content_layout.addWidget(self.error_label)

        content_layout.addSpacing(8)

        # Page count
        self.page_count_label = QLabel("")
        self.page_count_label.setObjectName("page_count")
        self.page_count_label.hide()
        content_layout.addWidget(self.page_count_label)

        content_layout.addSpacing(16)

        # ── Preview panel ───────────────────────────────
        preview_header = QLabel("PREVIEW")
        preview_header.setObjectName("section_label")
        preview_header.hide()
        self.preview_header = preview_header
        content_layout.addWidget(preview_header)

        content_layout.addSpacing(8)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(200)
        self.preview_text.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.preview_text.hide()
        content_layout.addWidget(self.preview_text)

        main_layout.addWidget(content)

    # ── Handlers ─────────────────────────────────────────
    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document",
            "",
            "Documents (*.pdf *.txt *.docx)"
        )
        if file_path:
            self._process_file(file_path)

    def _process_file(self, file_path: str):
        """Save the file to uploads dir, extract, and preview."""
        self.error_label.hide()
        self.status_label.hide()
        self.page_count_label.hide()
        self.preview_header.hide()
        self.preview_text.hide()

        try:
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            # Copy file to upload directory
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(
                UPLOAD_DIR, file_name
            )

            # Only copy if source != destination
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                with open(file_path, "rb") as src:
                    with open(dest_path, "wb") as dst:
                        dst.write(src.read())

            document = DocumentFactory.create_document(
                dest_path
            )
            extracted_pages = document.extract_text()

            # Show results
            self.status_label.setText(
                f"Document processed — {file_name}"
            )
            self.status_label.show()

            self.page_count_label.setText(
                f"Pages extracted: {len(extracted_pages)}"
            )
            self.page_count_label.show()

            self.preview_header.show()

            preview_content = (
                extracted_pages[0]["text"][:2000]
            )
            self.preview_text.setPlainText(preview_content)
            self.preview_text.show()

        except Exception as e:
            self.error_label.setText(str(e))
            self.error_label.show()

    def reset(self):
        """Reset page state (on logout)."""
        self.status_label.hide()
        self.error_label.hide()
        self.page_count_label.hide()
        self.preview_header.hide()
        self.preview_text.clear()
        self.preview_text.hide()
        self.greeting_label.setText("Welcome")
