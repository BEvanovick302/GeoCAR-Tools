"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: main.py
Versão......: 4.0
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Inicialização da aplicação.
===============================================================================
"""

import sys

from PySide6.QtWidgets import QApplication

from app.core.app_state import AppState
from app.main_window import MainWindow


def main():
    """
    Inicializa a aplicação.
    """

    app = QApplication(sys.argv)

    app.setApplicationName(
        "GeoCAR Tools"
    )

    app.setOrganizationName(
        "GeoCAR"
    )

    state = AppState()

    window = MainWindow(
        state=state
    )

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()