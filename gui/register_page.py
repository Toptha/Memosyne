"""Register page — username, email, password, confirm password."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from modules.auth.auth import Authentication


class RegisterPage(QWidget):
    """Registration form widget."""

    register_success = pyqtSignal()
    navigate_login = pyqtSignal()

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

        subtitle = QLabel("Create your account")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(32)

        # ── Username ────────────────────────────────────
        username_label = QLabel("Username")
        username_label.setObjectName("section_label")
        card_layout.addWidget(username_label)
        card_layout.addSpacing(6)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(18)

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
        self.password_input.setPlaceholderText("At least 8 characters")
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(18)

        # ── Confirm Password ────────────────────────────
        confirm_label = QLabel("Confirm Password")
        confirm_label.setObjectName("section_label")
        card_layout.addWidget(confirm_label)
        card_layout.addSpacing(6)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Re-enter your password")
        self.confirm_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        card_layout.addWidget(self.confirm_input)

        card_layout.addSpacing(12)

        # ── Message labels (hidden by default) ──────────
        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        self.success_label = QLabel("")
        self.success_label.setObjectName("success_label")
        self.success_label.setWordWrap(True)
        self.success_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.success_label.hide()
        card_layout.addWidget(self.success_label)

        card_layout.addSpacing(24)

        # ── Register button ─────────────────────────────
        register_btn = QPushButton("Create Account")
        register_btn.setObjectName("primary_btn")
        register_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        register_btn.clicked.connect(self._on_register)
        card_layout.addWidget(register_btn)

        card_layout.addSpacing(20)

        # ── Divider ─────────────────────────────────────
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        card_layout.addWidget(divider)

        card_layout.addSpacing(20)

        # ── Login link ──────────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_label = QLabel("Already have an account?")
        info_label.setStyleSheet("color: #666666; font-size: 13px;")
        bottom_row.addWidget(info_label)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("link_btn")
        login_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        login_btn.clicked.connect(
            self.navigate_login.emit
        )
        bottom_row.addWidget(login_btn)

        card_layout.addLayout(bottom_row)

        outer.addWidget(card)

    # ── Handlers ─────────────────────────────────────────
    def _on_register(self):
        """Validate inputs and call Authentication.register()."""
        self.error_label.hide()
        self.success_label.hide()

        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not all([username, email, password, confirm]):
            self._show_error("Please fill in all fields.")
            return

        try:
            Authentication.register(
                username, email, password, confirm
            )

            self._show_success(
                "Registration successful! Redirecting to login..."
            )

            # Emit signal after a short visual pause
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(
                1200, self.register_success.emit
            )

        except Exception as e:
            self._show_error(str(e))

    def _show_error(self, message: str):
        self.success_label.hide()
        self.error_label.setText(message)
        self.error_label.show()

    def _show_success(self, message: str):
        self.error_label.hide()
        self.success_label.setText(message)
        self.success_label.show()

    def reset(self):
        """Clear all fields and hide messages."""
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.error_label.hide()
        self.success_label.hide()
