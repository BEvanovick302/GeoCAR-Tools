"""
===============================================================================
GeoCAR Tools
Versão 3.0
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

from app.exporter import Exporter
from app.importer import Importer
from app.json_reader import JsonReader
from app.json_reporter import JsonReporter
from app.json_validator import JsonValidator


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GeoCAR Tools - V3.0")
        self.resize(1320, 920)
        self.setMinimumSize(1050, 720)

        self.data = None
        self.filename = None

        self.json_data = None
        self.json_filename = None
        self.json_summary = None
        self.json_layers = {}
        self.json_validation = {}
        self.json_validation_summary = None

        self.create_ui()

    def create_ui(self):

        central = QWidget()
        layout = QVBoxLayout(central)

        titulo = QLabel("🌎 GeoCAR Tools")
        titulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        titulo.setStyleSheet(
            """
            font-size: 26px;
            font-weight: bold;
            padding: 10px;
            """
        )

        subtitulo = QLabel(
            "Validação de Shapefile e conversão de JSON do SICAR"
        )
        subtitulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        botoes = QHBoxLayout()

        self.button_import = QPushButton(
            "Importar Shapefile"
        )
        self.button_import.clicked.connect(
            self.import_shape
        )

        self.button_json = QPushButton(
            "Importar JSON SICAR"
        )
        self.button_json.clicked.connect(
            self.import_json
        )

        self.button_validate_json = QPushButton(
            "Validar JSON"
        )
        self.button_validate_json.setEnabled(False)
        self.button_validate_json.clicked.connect(
            self.validate_json_layers
        )

        self.button_export_json = QPushButton(
            "Exportar Camadas SICAR"
        )
        self.button_export_json.setEnabled(False)
        self.button_export_json.clicked.connect(
            self.export_json_layers
        )

        self.button_json_report = QPushButton(
            "Relatório JSON"
        )
        self.button_json_report.setEnabled(False)
        self.button_json_report.clicked.connect(
            self.export_json_report
        )

        self.button_fix = QPushButton(
            "Corrigir Geometrias"
        )
        self.button_fix.setEnabled(False)
        self.button_fix.clicked.connect(
            self.fix_geometries
        )

        self.button_export = QPushButton(
            "Relatório Shapefile"
        )
        self.button_export.setEnabled(False)
        self.button_export.clicked.connect(
            self.export_report
        )

        self.button_clear = QPushButton(
            "Limpar"
        )
        self.button_clear.setEnabled(False)
        self.button_clear.clicked.connect(
            self.clear_results
        )

        botoes.addWidget(self.button_import)
        botoes.addWidget(self.button_json)
        botoes.addWidget(self.button_validate_json)
        botoes.addWidget(self.button_export_json)
        botoes.addWidget(self.button_json_report)
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
            "Resultado",
        ]

        self.table = QTableWidget(
            len(self.fields),
            2,
        )

        self.table.setHorizontalHeaderLabels(
            ["Campo", "Valor"]
        )

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.table.verticalHeader().setVisible(False)

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setAlternatingRowColors(True)

        for linha, campo in enumerate(self.fields):

            self.table.setItem(
                linha,
                0,
                QTableWidgetItem(campo),
            )

            self.table.setItem(
                linha,
                1,
                QTableWidgetItem("-"),
            )

        self.table.resizeColumnsToContents()

        self.lbl_json = QLabel(
            "JSON SICAR: nenhum arquivo carregado."
        )
        self.lbl_json.setWordWrap(True)

        self.lbl_json_validation = QLabel(
            "Validação JSON: não executada."
        )
        self.lbl_json_validation.setWordWrap(True)

        self.lbl_status = QLabel(
            "Status: aguardando seleção."
        )
        self.lbl_status.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addLayout(botoes)
        layout.addWidget(self.table)
        layout.addWidget(self.lbl_json)
        layout.addWidget(self.lbl_json_validation)
        layout.addWidget(self.lbl_status)

        self.setCentralWidget(central)

    def import_shape(self):

        filename = Importer.select_shapefile(
            self
        )

        if not filename:

            self.lbl_status.setText(
                "Status: operação cancelada."
            )

            return

        try:

            self.filename = filename

            self.data = Importer.load_shapefile(
                filename
            )

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

            QMessageBox.critical(
                self,
                "Erro ao carregar Shapefile",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: erro ao carregar Shapefile."
            )

    def import_json(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo JSON do SICAR",
            "",
            "Arquivo JSON (*.json)",
        )

        if not filename:

            self.lbl_status.setText(
                "Status: importação do JSON cancelada."
            )

            return

        try:

            json_data = JsonReader.open(
                filename
            )

            json_layers = JsonReader.extract_layers(
                json_data
            )

            summary = JsonReader.summary(
                json_data
            )

            self.json_filename = filename
            self.json_data = json_data
            self.json_layers = json_layers
            self.json_summary = summary
            self.json_validation = {}
            self.json_validation_summary = None

            layer_names = sorted(
                json_layers.keys()
            )

            layers_text = (
                ", ".join(layer_names)
                if layer_names
                else "Nenhuma camada encontrada"
            )

            self.lbl_json.setText(
                f"JSON SICAR: {os.path.basename(filename)} | "
                f"Camadas: {len(layer_names)} | "
                f"Geometrias: {summary['geometry_count']} | "
                f"{layers_text}"
            )

            self.lbl_json_validation.setText(
                "Validação JSON: não executada."
            )

            self.button_validate_json.setEnabled(
                bool(json_layers)
            )

            self.button_export_json.setEnabled(
                bool(json_layers)
            )

            self.button_json_report.setEnabled(False)
            self.button_clear.setEnabled(True)

            QMessageBox.information(
                self,
                "JSON SICAR carregado",
                (
                    f"Arquivo: "
                    f"{os.path.basename(filename)}\n\n"
                    f"Camadas oficiais encontradas: "
                    f"{len(layer_names)}\n"
                    f"Geometrias encontradas: "
                    f"{summary['geometry_count']}\n"
                    f"Polígonos: "
                    f"{summary['polygon_count']}\n"
                    f"MultiPolígonos: "
                    f"{summary['multipolygon_count']}\n"
                    f"Pontos: "
                    f"{summary['point_count']}\n"
                    f"Linhas: "
                    f"{summary['line_count']}\n\n"
                    f"{self._format_layers(layer_names)}"
                ),
            )

            self.lbl_status.setText(
                f"Status: JSON SICAR "
                f"{os.path.basename(filename)} "
                "carregado com sucesso."
            )

        except Exception as erro:

            self.json_data = None
            self.json_filename = None
            self.json_layers = {}
            self.json_summary = None
            self.json_validation = {}
            self.json_validation_summary = None

            self.button_validate_json.setEnabled(False)
            self.button_export_json.setEnabled(False)
            self.button_json_report.setEnabled(False)

            QMessageBox.critical(
                self,
                "Erro ao carregar JSON",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: erro ao carregar JSON."
            )

    def validate_json_layers(self):

        if not self.json_layers:
            return

        try:

            results = JsonValidator.validate_layers(
                self.json_layers
            )

            summary = JsonValidator.create_summary(
                results
            )

            self.json_validation = results
            self.json_validation_summary = summary

            self.button_json_report.setEnabled(True)

            self.lbl_json_validation.setText(
                "Validação JSON: "
                f"{summary['overall_result']} | "
                f"Camadas: {summary['layer_count']} | "
                f"Aprovadas: {summary['approved_layers']} | "
                f"Requer atenção: "
                f"{summary['attention_layers']} | "
                f"Inválidas: {summary['invalid_count']} | "
                f"Nulas: {summary['null_count']} | "
                f"Vazias: {summary['empty_count']} | "
                f"Duplicadas: {summary['duplicate_count']}"
            )

            QMessageBox.information(
                self,
                "Validação do JSON",
                self._format_validation_report(
                    results,
                    summary,
                ),
            )

            self.lbl_status.setText(
                "Status: validação das camadas JSON concluída."
            )

        except Exception as erro:

            self.button_json_report.setEnabled(False)

            QMessageBox.critical(
                self,
                "Erro na validação",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: erro ao validar camadas JSON."
            )
            
    def fix_geometries(self):

        if not self.filename:
            return

        try:

            output = Importer.fix_invalid_geometries(
                self,
                self.filename,
            )

            if not output:
                return

            self.filename = output

            self.data = Importer.load_shapefile(
                output
            )

            self.update_table()

            self.button_fix.setEnabled(
                self.data["invalid_count"] > 0
            )

            QMessageBox.information(
                self,
                "GeoCAR Tools",
                "Geometrias corrigidas com sucesso.",
            )

            self.lbl_status.setText(
                f"Status: arquivo corrigido salvo em {output}"
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro ao corrigir",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: erro ao corrigir geometrias."
            )
            
    def export_report(self):

        if not self.filename or not self.data:
            return

        nome = os.path.splitext(
            os.path.basename(self.filename)
        )[0]

        output, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatório",
            f"relatorio_{nome}.txt",
            "Arquivo de texto (*.txt)",
        )

        if not output:
            return

        if not output.lower().endswith(".txt"):
            output += ".txt"

        try:

            with open(
                output,
                "w",
                encoding="utf-8",
            ) as arquivo:

                valores = [
                    os.path.basename(self.filename),
                    self.data["components"],
                    self.data["missing_components"],
                    self.data["crs"],
                    self.data["calculation_crs"],
                    self.data["features"],
                    self.data["geometry"],
                    self.data["geometry_types"],
                    self.data["area_ha"],
                    self.data["perimeter_m"],
                    "Sim" if self.data["is_valid"] else "Não",
                    self.data["invalid_count"],
                    self.data["null_count"],
                    self.data["empty_count"],
                    self.data["multipart_count"],
                    self.data["interior_rings_count"],
                    self.data["duplicate_count"],
                    self.data["overall_result"],
                ]

                for campo, valor in zip(
                    self.fields,
                    valores,
                ):
                    arquivo.write(
                        f"{campo}: {valor}\n"
                    )

            QMessageBox.information(
                self,
                "Relatório exportado",
                "Relatório salvo com sucesso.",
            )

            self.lbl_status.setText(
                f"Status: relatório salvo em {output}"
            )

        except OSError as erro:

            QMessageBox.critical(
                self,
                "Erro ao exportar relatório",
                str(erro),
            )

            self.lbl_status.setText(
                "Status: erro ao exportar relatório."
            )
            
    def export_json_layers(self):

        if not self.json_layers:
            return

        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de saída",
        )

        if not output_dir:
            return

        try:

            exported = Exporter.export_layers_as_shapefiles(
                self.json_layers,
                output_dir,
            )

            gpkg_path = os.path.join(
                output_dir,
                "GeoCAR_Tools_SICAR.gpkg",
            )

            Exporter.export_geopackage(
                self.json_layers,
                gpkg_path,
            )

            QMessageBox.information(
                self,
                "Exportação concluída",
                (
                    f"{len(exported)} camada(s) exportada(s).\n\n"
                    f"GeoPackage criado:\n{gpkg_path}"
                ),
            )

            self.lbl_status.setText(
                "Status: exportação do SICAR concluída."
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro),
            )

    def export_json_report(self):

        if (
            not self.json_filename
            or not self.json_validation_summary
        ):
            return

        nome = os.path.splitext(
            os.path.basename(
                self.json_filename
            )
        )[0]

        output, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatório",
            f"{nome}_relatorio_json.txt",
            "Arquivo Texto (*.txt)",
        )

        if not output:
            return

        try:

            JsonReporter.export_report(
                self.json_filename,
                self.json_validation,
                self.json_validation_summary,
                output,
            )

            QMessageBox.information(
                self,
                "Relatório",
                "Relatório exportado com sucesso.",
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro),
            )

    def clear_results(self):

        self.data = None
        self.filename = None

        self.json_data = None
        self.json_filename = None
        self.json_summary = None
        self.json_layers = {}
        self.json_validation = {}
        self.json_validation_summary = None

        for linha in range(len(self.fields)):
            self.table.item(
                linha,
                1,
            ).setText("-")

        self.lbl_json.setText(
            "JSON SICAR: nenhum arquivo carregado."
        )

        self.lbl_json_validation.setText(
            "Validação JSON: não executada."
        )

        self.button_export.setEnabled(False)
        self.button_fix.setEnabled(False)
        self.button_export_json.setEnabled(False)
        self.button_validate_json.setEnabled(False)
        self.button_json_report.setEnabled(False)
        self.button_clear.setEnabled(False)

        self.lbl_status.setText(
            "Status: resultados limpos."
        )

    def update_table(self):

        if not self.data:
            return

        valores = [

            os.path.basename(self.filename),

            self.data["components"],

            self.data["missing_components"],

            self.data["crs"],

            self.data["calculation_crs"],

            self.data["features"],

            self.data["geometry"],

            self.data["geometry_types"],

            self.data["area_ha"],

            self.data["perimeter_m"],

            "Sim"
            if self.data["is_valid"]
            else "Não",

            self.data["invalid_count"],

            self.data["null_count"],

            self.data["empty_count"],

            self.data["multipart_count"],

            self.data["interior_rings_count"],

            self.data["duplicate_count"],

            self.data["overall_result"],

        ]

        for linha, valor in enumerate(valores):

            self.table.item(
                linha,
                1,
            ).setText(str(valor))

    def _format_validation_report(
        self,
        results,
        summary,
    ):

        linhas = [

            f"Resultado Geral: {summary['overall_result']}",

            f"Camadas: {summary['layer_count']}",

            f"Feições: {summary['feature_count']}",

            "",

        ]

        for nome, dados in results.items():

            linhas.extend(

                [

                    f"{nome}",

                    f"   Resultado: {dados['result']}",

                    f"   Feições: {dados['features']}",

                    f"   Geometrias: {dados['geometry_types']}",

                    f"   Inválidas: {dados['invalid_count']}",

                    f"   Multipartes: {dados['multipart_count']}",

                    "",

                ]

            )

        return "\n".join(linhas)

    @staticmethod
    def _format_layers(layers):

        if not layers:
            return "Nenhuma camada."

        return "\n".join(
            f"• {layer}"
            for layer in layers
        )