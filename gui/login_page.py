"""Login page — email + password form with navigation to Register."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from modules.auth.auth import Authentication


class LoginPage(QWidget):
    """Login form widget with email/password inputs."""

    login_success = pyqtSignal(str, str)   # username, email
    navigate_register = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ── UI Construction ──────────────────────────────────
    def _build_ui(self):

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(0, 0, 0, 0)

        # Card container
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 48, 40, 40)
        card_layout.setSpacing(0)

        # ── Title ────────────────────────────────────────
        title = QLabel("Mnemosyne")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        card_layout.addSpacing(6)

        subtitle = QLabel("Sign in to continue")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(32)

        # ── Email ────────────────────────────────────────
        email_label = QLabel("Email")
        email_label.setObjectName("section_label")
        card_layout.addWidget(email_label)
        card_layout.addSpacing(6)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@example.com")
        card_layout.addWidget(self.email_input)

        card_layout.addSpacing(18)

        # ── Password ────────────────────────────────────
        password_label = QLabel("Password")
        password_label.setObjectName("section_label")
        card_layout.addWidget(password_label)
        card_layout.addSpacing(6)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(12)

        # ── Error label (hidden by default) ─────────────
        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        card_layout.addSpacing(24)

        # ── Login button ────────────────────────────────
        login_btn = QPushButton("Login")
        login_btn.setObjectName("primary_btn")
        login_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(login_btn)

        card_layout.addSpacing(20)

        # ── Divider ─────────────────────────────────────
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        card_layout.addWidget(divider)

        card_layout.addSpacing(20)

        # ── Register link ───────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_label = QLabel("Don't have an account?")
        info_label.setStyleSheet("color: #666666; font-size: 13px;")
        bottom_row.addWidget(info_label)

        register_btn = QPushButton("Register")
        register_btn.setObjectName("link_btn")
        register_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        register_btn.clicked.connect(
            self.navigate_register.emit
        )
        bottom_row.addWidget(register_btn)

        card_layout.addLayout(bottom_row)

        outer.addWidget(card)

    # ── Handlers ─────────────────────────────────────────
    def _on_login(self):
        """Validate inputs and call Authentication.login()."""
        self.error_label.hide()

        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self._show_error("Please fill in all fields.")
            return

        try:
            user = Authentication.login(email, password)
            # user tuple: (id, username, email, password, created_at)
            self.login_success.emit(user[1], user[2])

        except Exception as e:
            self._show_error(str(e))

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()

    def reset(self):
        """Clear all fields and hide messages."""
        self.email_input.clear()
        self.password_input.clear()
        self.error_label.hide()
