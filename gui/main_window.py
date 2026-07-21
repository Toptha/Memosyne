"""Main application window — hosts all pages in a stacked widget."""

from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget
)
from PyQt6.QtCore import Qt

from gui.theme import STYLESHEET
from gui.login_page import LoginPage
from gui.register_page import RegisterPage
from gui.home_page import HomePage
from gui.arxiv_page import ArxivPage


class MnemosyneApp(QMainWindow):
    """Root window managing page navigation."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mnemosyne")
        self.setMinimumSize(900, 650)
        self.resize(1050, 720)

        # Apply global theme
        self.setStyleSheet(STYLESHEET)

        # ── Stacked widget (page container) ─────────────
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ── Create pages ────────────────────────────────
        self.login_page = LoginPage()
        self.register_page = RegisterPage()
        self.home_page = HomePage()
        self.arxiv_page = ArxivPage()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.arxiv_page)

        # ── Wire signals ────────────────────────────────
        # Login → Home
        self.login_page.login_success.connect(
            self._on_login_success
        )

        # Login ↔ Register navigation
        self.login_page.navigate_register.connect(
            lambda: self._go_to(self.register_page)
        )
        self.register_page.navigate_login.connect(
            lambda: self._go_to(self.login_page)
        )

        # Register success → Login
        self.register_page.register_success.connect(
            lambda: self._go_to(self.login_page)
        )

        # Logout → Login
        self.home_page.logout_requested.connect(
            self._on_logout
        )

        # Home ↔ Arxiv navigation
        self.home_page.navigate_arxiv.connect(
            self._on_navigate_arxiv
        )
        self.arxiv_page.navigate_home.connect(
            lambda: self._go_to(self.home_page)
        )

        # Start on login page
        self.stack.setCurrentWidget(self.login_page)

    # ── Navigation helpers ───────────────────────────────
    def _go_to(self, page):
        """Switch the visible page."""
        page.reset()
        self.stack.setCurrentWidget(page)

    def _on_login_success(self, username: str, email: str):
        """Handle successful login — switch to home."""
        self.username = username
        self.home_page.set_user(username, email)
        self.stack.setCurrentWidget(self.home_page)

    def _on_navigate_arxiv(self):
        """Handle navigating to the arXiv search page."""
        self.arxiv_page.set_user(self.username)
        self._go_to(self.arxiv_page)

    def _on_logout(self):
        """Handle logout — reset and return to login."""
        self.home_page.reset()
        self.login_page.reset()
        self.stack.setCurrentWidget(self.login_page)
