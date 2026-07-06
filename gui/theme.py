"""
Mnemosyne — NotebookLM-inspired dark theme (QSS stylesheet).

Palette:
    Background   #1A1A1A
    Surface      #242424
    Surface Hover #2E2E2E
    Border       #3A3A3A
    Text Primary #FFFFFF
    Text Muted   #A0A0A0
    Accent       #FFFFFF
    Error        #FF6B6B
    Success      #4ADE80
"""

STYLESHEET = """

/* ── Global ──────────────────────────────────────────── */
QMainWindow, QWidget {
    background-color: #1A1A1A;
    color: #FFFFFF;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
}

/* ── QLabel ──────────────────────────────────────────── */
QLabel {
    color: #FFFFFF;
    background: transparent;
}

QLabel#title {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#subtitle {
    font-size: 18px;
    font-weight: 500;
    color: #A0A0A0;
}

QLabel#greeting {
    font-size: 16px;
    color: #A0A0A0;
}

QLabel#error_label {
    color: #FF6B6B;
    font-size: 13px;
    padding: 8px 12px;
    background-color: rgba(255, 107, 107, 0.08);
    border: 1px solid rgba(255, 107, 107, 0.25);
    border-radius: 8px;
}

QLabel#success_label {
    color: #4ADE80;
    font-size: 13px;
    padding: 8px 12px;
    background-color: rgba(74, 222, 128, 0.08);
    border: 1px solid rgba(74, 222, 128, 0.25);
    border-radius: 8px;
}

QLabel#section_label {
    font-size: 13px;
    font-weight: 600;
    color: #A0A0A0;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#page_count {
    font-size: 14px;
    color: #A0A0A0;
}

QLabel#drop_icon {
    font-size: 42px;
    color: #555555;
}

QLabel#drop_text {
    font-size: 14px;
    color: #888888;
}

QLabel#drop_hint {
    font-size: 12px;
    color: #555555;
}

/* ── QLineEdit ───────────────────────────────────────── */
QLineEdit {
    background-color: #242424;
    color: #FFFFFF;
    border: 1px solid #3A3A3A;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: #555555;
}

QLineEdit:focus {
    border: 1px solid #FFFFFF;
}

QLineEdit::placeholder {
    color: #666666;
}

/* ── QPushButton ─────────────────────────────────────── */
QPushButton#primary_btn {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton#primary_btn:hover {
    background-color: #E0E0E0;
}

QPushButton#primary_btn:pressed {
    background-color: #CCCCCC;
}

QPushButton#secondary_btn {
    background-color: transparent;
    color: #FFFFFF;
    border: 1px solid #3A3A3A;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton#secondary_btn:hover {
    background-color: #2E2E2E;
    border-color: #555555;
}

QPushButton#secondary_btn:pressed {
    background-color: #242424;
}

QPushButton#link_btn {
    background: transparent;
    color: #A0A0A0;
    border: none;
    font-size: 13px;
    text-decoration: underline;
    padding: 4px;
}

QPushButton#link_btn:hover {
    color: #FFFFFF;
}

QPushButton#logout_btn {
    background-color: transparent;
    color: #A0A0A0;
    border: 1px solid #3A3A3A;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton#logout_btn:hover {
    color: #FFFFFF;
    border-color: #555555;
    background-color: #2E2E2E;
}

QPushButton#upload_btn {
    background-color: #242424;
    color: #FFFFFF;
    border: 1px solid #3A3A3A;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton#upload_btn:hover {
    background-color: #2E2E2E;
    border-color: #555555;
}

/* ── QTextEdit (preview panel) ───────────────────────── */
QTextEdit {
    background-color: #242424;
    color: #D0D0D0;
    border: 1px solid #3A3A3A;
    border-radius: 8px;
    padding: 16px;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 13px;
    selection-background-color: #555555;
}

/* ── QFrame (dividers / cards) ───────────────────────── */
QFrame#divider {
    background-color: #3A3A3A;
    max-height: 1px;
    min-height: 1px;
}

QFrame#card {
    background-color: #242424;
    border: 1px solid #3A3A3A;
    border-radius: 12px;
}

QFrame#drop_zone {
    background-color: #242424;
    border: 2px dashed #3A3A3A;
    border-radius: 12px;
}

QFrame#drop_zone[dragActive="true"] {
    border-color: #FFFFFF;
    background-color: #2E2E2E;
}

QFrame#header_bar {
    background-color: #1A1A1A;
    border-bottom: 1px solid #3A3A3A;
}

/* ── QScrollBar ──────────────────────────────────────── */
QScrollBar:vertical {
    background: #1A1A1A;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #3A3A3A;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #555555;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #1A1A1A;
    height: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #3A3A3A;
    min-width: 30px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #555555;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}
"""
