"""Arxiv search page for finding research papers."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QLineEdit,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

from modules.search.arxiv_search import ArxivSearch

class ArxivPage(QWidget):
    """View for searching and displaying arXiv papers."""
    
    navigate_home = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._username = ""
        self.search_backend = ArxivSearch()
        self._build_ui()

    def set_user(self, username: str):
        """Set the logged-in user details for the header."""
        self._username = username
        self.greeting_label.setText(f"Welcome, {username}")

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

        app_title = QLabel("Mnemosyne - arXiv")
        app_title.setStyleSheet(
            "font-size: 18px; font-weight: 700; letter-spacing: 1px;"
        )
        header_layout.addWidget(app_title)

        header_layout.addStretch()

        self.greeting_label = QLabel("Welcome")
        self.greeting_label.setObjectName("greeting")
        header_layout.addWidget(self.greeting_label)

        header_layout.addSpacing(16)

        home_btn = QPushButton("Back to Home")
        home_btn.setObjectName("logout_btn") # Reusing logout button styling for consistency
        home_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        home_btn.clicked.connect(self.navigate_home.emit)
        header_layout.addWidget(home_btn)

        main_layout.addWidget(header)

        # ── Content area ────────────────────────────────
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 36, 48, 36)
        content_layout.setSpacing(16)

        section_title = QLabel("ARXIV PAPER SEARCH")
        section_title.setObjectName("section_label")
        content_layout.addWidget(section_title)
        
        section_desc = QLabel(
            "Search for research papers directly from arXiv to use in Mnemosyne."
        )
        section_desc.setStyleSheet("color: #666666; font-size: 13px;")
        content_layout.addWidget(section_desc)
        
        content_layout.addSpacing(8)

        # ── Search Bar ──────────────────────────────────
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter your search query (e.g., Physics-Informed Neural Networks)...")
        self.search_input.returnPressed.connect(self._perform_search)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("Search")
        search_btn.setObjectName("primary_btn")
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.clicked.connect(self._perform_search)
        search_layout.addWidget(search_btn)

        content_layout.addLayout(search_layout)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #A0A0A0; font-size: 13px;")
        content_layout.addWidget(self.status_label)

        # ── Results Area (Scrollable) ───────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(16)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.results_container)
        content_layout.addWidget(self.scroll_area)

        main_layout.addWidget(content)

    def _perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
            
        self._clear_results()
        self.status_label.setText("Searching arXiv...")
        self.repaint() # Force UI update immediately
        
        results = self.search_backend.search(query, max_results=5)
        
        if not results:
            self.status_label.setText("No papers found. Try a different query.")
            return
            
        self.status_label.setText(f"Found {len(results)} results for '{query}'")
        
        for paper in results:
            card = self._create_result_card(paper)
            self.results_layout.addWidget(card)
            
    def _create_result_card(self, paper: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        # Title
        title_label = QLabel(paper.get('Title', 'No Title'))
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        title_label.setWordWrap(True)
        card_layout.addWidget(title_label)
        
        # Authors and Date
        meta_label = QLabel(f"Authors: {paper.get('Authors', 'N/A')} • Published: {paper.get('Published', 'N/A')}")
        meta_label.setStyleSheet("font-size: 13px; color: #A0A0A0;")
        meta_label.setWordWrap(True)
        card_layout.addWidget(meta_label)
        
        # Summary
        summary = paper.get('Summary', 'No summary available.')
        # Truncate summary if too long
        if len(summary) > 300:
            summary = summary[:297] + "..."
            
        summary_label = QLabel(summary)
        summary_label.setStyleSheet("font-size: 13px; color: #D0D0D0; line-height: 1.4;")
        summary_label.setWordWrap(True)
        card_layout.addWidget(summary_label)
        
        # Actions Row (PDF Button)
        action_layout = QHBoxLayout()
        pdf_link = paper.get('PDF')
        if pdf_link and pdf_link != "Not available":
            pdf_btn = QPushButton("Open PDF")
            pdf_btn.setObjectName("secondary_btn")
            pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Use a default argument in the lambda to capture the current pdf_link value
            pdf_btn.clicked.connect(lambda checked, link=pdf_link: QDesktopServices.openUrl(QUrl(link)))
            action_layout.addWidget(pdf_btn)
            
        action_layout.addStretch()
        card_layout.addLayout(action_layout)
        
        return card

    def _clear_results(self):
        # Remove all widgets from the results layout
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def reset(self):
        """Reset page state when returning to it."""
        self.search_input.clear()
        self.status_label.clear()
        self._clear_results()
