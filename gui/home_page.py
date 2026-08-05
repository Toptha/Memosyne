"""Home page — document upload, extraction, indexing, and Q&A."""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit,
    QLineEdit, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from modules.extractor import DocumentFactory
from engine.pipelines.indexing_pipeline import ingest_file
from engine.pipelines.search_pipeline import ask_with_memory
from engine.conversation.memory import ConversationMemory
from engine.embeddings.vector_store import list_documents

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
    navigate_arxiv = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._username = ""
        self._email = ""
        # One conversation session per HomePage instance - cleared
        # on logout via reset(). NOTE: this is in-memory only, so
        # history resets if the app restarts (matches memory.py's
        # current no-persistence design).
        self.memory = ConversationMemory()
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

        search_arxiv_btn = QPushButton("Search arXiv")
        search_arxiv_btn.setObjectName("logout_btn")
        search_arxiv_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_arxiv_btn.clicked.connect(self.navigate_arxiv.emit)
        header_layout.addWidget(search_arxiv_btn)

        header_layout.addSpacing(8)

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
            "Upload a document to extract, index, and ask questions about it"
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

        content_layout.addSpacing(16)

        # ── Indexed documents list ──────────────────────
        docs_header = QLabel("YOUR DOCUMENTS")
        docs_header.setObjectName("section_label")
        content_layout.addWidget(docs_header)

        content_layout.addSpacing(6)

        self.documents_list_label = QLabel("No documents indexed yet.")
        self.documents_list_label.setObjectName("page_count")
        self.documents_list_label.setWordWrap(True)
        content_layout.addWidget(self.documents_list_label)

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
        self.preview_text.setMinimumHeight(150)
        self.preview_text.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.preview_text.hide()
        content_layout.addWidget(self.preview_text)

        content_layout.addSpacing(20)

        # ── Ask panel ────────────────────────────────────
        ask_header = QLabel("ASK A QUESTION")
        ask_header.setObjectName("section_label")
        content_layout.addWidget(ask_header)

        content_layout.addSpacing(8)

        ask_row = QHBoxLayout()

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText(
            "Ask something about your uploaded documents..."
        )
        self.question_input.returnPressed.connect(self._ask_question)
        ask_row.addWidget(self.question_input)

        ask_btn = QPushButton("Ask")
        ask_btn.setObjectName("upload_btn")
        ask_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ask_btn.clicked.connect(self._ask_question)
        ask_row.addWidget(ask_btn)

        content_layout.addLayout(ask_row)

        content_layout.addSpacing(12)

        self.answer_text = QTextEdit()
        self.answer_text.setReadOnly(True)
        self.answer_text.setMinimumHeight(180)
        self.answer_text.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.answer_text.setPlaceholderText(
            "Answers will appear here, grounded in your uploaded documents."
        )
        content_layout.addWidget(self.answer_text)

        main_layout.addWidget(content)

        self._refresh_documents_list()

    def _refresh_documents_list(self):
        """
        Pulls the current set of indexed documents from the vector
        store and updates the "YOUR DOCUMENTS" label. This is what
        makes it visible that earlier uploads are still searchable
        even after a newer file's preview has taken over the panel
        above - uploading a new file does NOT remove old ones from
        the index, it just changes what's shown in the preview.
        """
        try:
            docs = list_documents()
        except Exception:
            # vector store might not exist yet on a totally fresh install
            docs = []

        if not docs:
            self.documents_list_label.setText("No documents indexed yet.")
            return

        lines = [f"• {d['document_id']} ({d['chunk_count']} chunks)" for d in docs]
        self.documents_list_label.setText(
            f"{len(docs)} document(s) indexed and searchable:\n" + "\n".join(lines)
        )

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
        """Save the file to uploads dir, extract+preview, then index for search."""
        self.error_label.hide()
        self.status_label.hide()
        self.page_count_label.hide()
        self.preview_header.hide()
        self.preview_text.hide()

        try:
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            file_name = os.path.basename(file_path)
            dest_path = os.path.join(
                UPLOAD_DIR, file_name
            )

            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                with open(file_path, "rb") as src:
                    with open(dest_path, "wb") as dst:
                        dst.write(src.read())

            # existing preview extraction (unchanged)
            document = DocumentFactory.create_document(
                dest_path
            )
            extracted_pages = document.extract_text()

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

            # ── Index into the search engine ────────────
            # NOTE: this runs synchronously and will briefly freeze
            # the UI while embedding happens (a few seconds on this
            # hardware). Fine for now; move to a QThread/worker if
            # it feels too janky once you're testing with real use.
            self.status_label.setText(
                f"Document processed — {file_name} (indexing for search...)"
            )
            index_result = ingest_file(dest_path)

            if index_result["status"] == "ok":
                self.status_label.setText(
                    f"Document processed — {file_name} "
                    f"({index_result['chunk_count']} chunks indexed, ready to search)"
                )
                self._refresh_documents_list()
            else:
                # preview still worked, but indexing failed - surface
                # this without blowing away the preview that DID work
                self.error_label.setText(
                    f"Indexed preview only — search indexing failed: {index_result['error']}"
                )
                self.error_label.show()

        except Exception as e:
            self.error_label.setText(str(e))
            self.error_label.show()

    def _ask_question(self):
        """Send the question through the RAG pipeline and display the grounded answer."""
        question = self.question_input.text().strip()
        if not question:
            return

        self.answer_text.setPlainText("Thinking...")
        self.question_input.setEnabled(False)

        try:
            # NOTE: synchronous call - retrieval + generation take a
            # few seconds on this hardware, UI will be unresponsive
            # during that window. Same tradeoff as indexing above;
            # move to QThread together with ingestion later.
            result = ask_with_memory(self.memory, question)

            display_text = result["answer"]
            if result["sources_block"]:
                display_text += "\n" + result["sources_block"]

            self.answer_text.setPlainText(display_text)
            self.question_input.clear()

        except RuntimeError as e:
            # e.g. Ollama not running
            self.answer_text.setPlainText(f"Error: {e}")
        except Exception as e:
            self.answer_text.setPlainText(f"Something went wrong: {e}")
        finally:
            self.question_input.setEnabled(True)
            self.question_input.setFocus()

    def reset(self):
        """Reset page state (on logout)."""
        self.status_label.hide()
        self.error_label.hide()
        self.page_count_label.hide()
        self.preview_header.hide()
        self.preview_text.clear()
        self.preview_text.hide()
        self.greeting_label.setText("Welcome")
        self.answer_text.clear()
        self.question_input.clear()
        # fresh conversation on logout - new user session starts clean
        self.memory.clear()