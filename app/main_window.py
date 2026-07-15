"""
===============================================================================
GeoCAR Tools
MVP v1.9
===============================================================================
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.importer import Importer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GeoCAR Tools - MVP v1.9")
        self.resize(1200, 900)

        self.data = None
        self.filename = None

        self.create_ui()

    def create_ui(self):

        central = QWidget()
        layout = QVBoxLayout(central)

        titulo = QLabel("🌎 GeoCAR Tools")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
            padding:10px;
        """)

        subtitulo = QLabel(
            "Validação automática de arquivos CAR"
        )
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        botoes = QHBoxLayout()

        self.button_import = QPushButton("Importar")
        self.button_import.clicked.connect(self.import_shape)

        self.button_fix = QPushButton("Corrigir")
        self.button_fix.setEnabled(False)
        self.button_fix.clicked.connect(self.fix_geometries)

        self.button_export = QPushButton("Relatório")
        self.button_export.setEnabled(False)
        self.button_export.clicked.connect(self.export_report)

        self.button_clear = QPushButton("Limpar")
        self.button_clear.setEnabled(False)
        self.button_clear.clicked.connect(self.clear_results)

        botoes.addWidget(self.button_import)
        botoes.addWidget(self.button_fix)
        botoes.addWidget(self.button_export)
        botoes.addWidget(self.button_clear)

        self.fields = [

            "Arquivo",
            "Componentes",
            "Arquivos ausentes",

            "CRS original",
            "CRS cálculo",

            "Feições",

            "Geometria principal",
            "Tipos",

            "Área (ha)",
            "Perímetro (m)",

            "Válido",

            "Inválidas",
            "Nulas",
            "Vazias",

            "Multipartes",
            "Buracos",

            "Duplicadas",

            "Resultado"

        ]

        self.table = QTableWidget(
            len(self.fields),
            2
        )

        self.table.setHorizontalHeaderLabels(
            ["Campo", "Valor"]
        )

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setAlternatingRowColors(True)

        for linha, campo in enumerate(self.fields):

            self.table.setItem(
                linha,
                0,
                QTableWidgetItem(campo)
            )

            self.table.setItem(
                linha,
                1,
                QTableWidgetItem("-")
            )

        self.table.resizeColumnsToContents()

        self.lbl_status = QLabel(
            "Status: Aguardando seleção."
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addLayout(botoes)
        layout.addWidget(self.table)
        layout.addWidget(self.lbl_status)

        self.setCentralWidget(central)

    def import_shape(self):

        filename = Importer.select_shapefile(self)

        if not filename:
            self.lbl_status.setText(
                "Status: Operação cancelada."
            )
            return

        try:
            self.filename = filename
            self.data = Importer.load_shapefile(filename)

            self.update_table()

            self.button_export.setEnabled(True)
            self.button_clear.setEnabled(True)
            self.button_fix.setEnabled(
                self.data["invalid_count"] > 0
            )

            self.lbl_status.setText(
                f"Status: {os.path.basename(filename)} "
                "carregado com sucesso."
            )

        except Exception as erro:
            self.data = None
            self.filename = None

            self.button_export.setEnabled(False)
            self.button_fix.setEnabled(False)
            self.button_clear.setEnabled(False)

            QMessageBox.critical(
                self,
                "Erro",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: Erro ao carregar shapefile."
            )

    def update_table(self):

        valores = [
            os.path.basename(self.filename),
            self.data["components"],
            self.data["missing_components"],
            self.data["crs"],
            self.data["calculation_crs"],
            str(self.data["features"]),
            self.data["geometry"],
            self.data["geometry_types"],
            f"{self.data['area_ha']:.2f}",
            f"{self.data['perimeter_m']:.2f}",
            "Sim" if self.data["is_valid"] else "Não",
            str(self.data["invalid_count"]),
            str(self.data["null_count"]),
            str(self.data["empty_count"]),
            str(self.data["multipart_count"]),
            str(self.data["interior_rings_count"]),
            str(self.data["duplicate_count"]),
            self.data["overall_result"],
        ]

        for linha, valor in enumerate(valores):
            self.table.item(linha, 1).setText(str(valor))

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def clear_results(self):

        self.data = None
        self.filename = None

        for linha in range(len(self.fields)):
            self.table.item(linha, 1).setText("-")

        self.button_export.setEnabled(False)
        self.button_fix.setEnabled(False)
        self.button_clear.setEnabled(False)

        self.lbl_status.setText(
            "Status: Resultados limpos."
        )

    def fix_geometries(self):

        if not self.filename:
            return

        try:
            output_path = Importer.fix_invalid_geometries(
                self,
                self.filename,
            )

            if not output_path:
                self.lbl_status.setText(
                    "Status: Correção cancelada."
                )
                return

            self.filename = output_path
            self.data = Importer.load_shapefile(output_path)

            self.update_table()

            self.button_fix.setEnabled(
                self.data["invalid_count"] > 0
            )

            QMessageBox.information(
                self,
                "Correção concluída",
                "Shapefile corrigido e salvo com sucesso.",
            )

            self.lbl_status.setText(
                f"Status: Arquivo corrigido salvo em {output_path}"
            )

        except Exception as erro:
            QMessageBox.critical(
                self,
                "Erro ao corrigir",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: Erro ao corrigir geometrias."
            )

    def export_report(self):

        if not self.data or not self.filename:
            return

        nome_base = os.path.splitext(
            os.path.basename(self.filename)
        )[0]

        report_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"relatorio_{nome_base}.txt",
            "Arquivo de texto (*.txt)",
        )

        if not report_path:
            self.lbl_status.setText(
                "Status: Exportação cancelada."
            )
            return

        if not report_path.lower().endswith(".txt"):
            report_path += ".txt"

        report = (
            "GeoCAR Tools\n"
            "Relatório de análise do Shapefile\n"
            "========================================\n\n"
            f"Arquivo: {os.path.basename(self.filename)}\n"
            f"Caminho: {self.filename}\n"
            f"Componentes encontrados: {self.data['components']}\n"
            f"Arquivos ausentes: {self.data['missing_components']}\n"
            f"CRS original: {self.data['crs']}\n"
            f"CRS usado nos cálculos: {self.data['calculation_crs']}\n"
            f"Feições: {self.data['features']}\n"
            f"Geometria principal: {self.data['geometry']}\n"
            f"Tipos de geometria: {self.data['geometry_types']}\n"
            f"Área total (ha): {self.data['area_ha']:.2f}\n"
            f"Perímetro total (m): {self.data['perimeter_m']:.2f}\n"
            f"Geometria válida: "
            f"{'Sim' if self.data['is_valid'] else 'Não'}\n"
            f"Geometrias inválidas: {self.data['invalid_count']}\n"
            f"Geometrias nulas: {self.data['null_count']}\n"
            f"Geometrias vazias: {self.data['empty_count']}\n"
            f"Geometrias multipartes: {self.data['multipart_count']}\n"
            f"Buracos internos: {self.data['interior_rings_count']}\n"
            f"Geometrias duplicadas: {self.data['duplicate_count']}\n"
            f"Resultado geral: {self.data['overall_result']}\n"
        )

        try:
            with open(report_path, "w", encoding="utf-8") as arquivo:
                arquivo.write(report)

            QMessageBox.information(
                self,
                "Relatório exportado",
                "Relatório salvo com sucesso.",
            )

            self.lbl_status.setText(
                f"Status: Relatório salvo em {report_path}"
            )

        except OSError as erro:
            QMessageBox.critical(
                self,
                "Erro ao exportar",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: Erro ao exportar relatório."
            )