"""Mnemosyne — Semantic Document Search System"""

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MnemosyneApp


def main():

    app = QApplication(sys.argv)

    window = MnemosyneApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()