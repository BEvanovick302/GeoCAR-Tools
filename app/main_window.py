"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: main_window.py
Versão......: MVP 0.1 - Build 001
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Janela principal da aplicação.
===============================================================================
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow


class MainWindow(QMainWindow):
    """
    Janela principal do GeoCAR Tools.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GeoCAR Tools")
        self.resize(900, 600)
        self.setMinimumSize(800, 500)

        self._create_ui()

    def _create_ui(self):
        """
        Cria a interface principal.
        """

        label = QLabel()

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label.setText(
            "🌎 GeoCAR Tools\n\n"
            "Sistema de Apoio ao Cadastro Ambiental Rural\n\n"
            "MVP 0.1 - Build 001"
        )

        self.setCentralWidget(label)