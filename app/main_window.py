"""
===============================================================================
GeoCAR Tools
Arquivo.....: app/main_window.py
Versão......: 4.1.1
===============================================================================
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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

from app.controllers.comparison_controller import (
    ComparisonController,
)
from app.controllers.json_controller import (
    JsonController,
)
from app.controllers.shapefile_controller import (
    ShapefileController,
)
from app.core.app_state import (
    AppState,
)
from app.exporter import Exporter
from app.exporters.report_exporter import (
    ReportExporter,
)


class MainWindow(QMainWindow):

    def __init__(
        self,
        state: AppState,
    ):
        super().__init__()

        self.state = state

        self.setWindowTitle(
            "GeoCAR Tools V4.1.1"
        )

        self.resize(
            1450,
            930,
        )

        self.create_ui()

    def create_ui(self):

        central = QWidget()

        layout = QVBoxLayout(
            central
        )

        titulo = QLabel(
            "🌎 GeoCAR Tools"
        )

        titulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        titulo.setStyleSheet(
            """
            font-size:28px;
            font-weight:bold;
            padding:10px;
            """
        )

        subtitulo = QLabel(
            "Validação • Comparação • Conversão • SICAR"
        )

        subtitulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        botoes1 = QHBoxLayout()
        botoes2 = QHBoxLayout()

        self.bt_import_shape = QPushButton(
            "Importar Shape"
        )
        self.bt_import_shape.clicked.connect(
            self.import_shapefile
        )

        self.bt_import_json = QPushButton(
            "Importar JSON"
        )
        self.bt_import_json.clicked.connect(
            self.import_json
        )

        self.cmb_layers = QComboBox()

        self.cmb_layers.setMinimumWidth(
            260
        )

        self.cmb_layers.setEnabled(
            False
        )

        self.cmb_layers.addItem(
            "Selecione uma camada..."
        )

        self.bt_compare = QPushButton(
            "Comparar"
        )

        self.bt_compare.setEnabled(
            False
        )

        self.bt_compare.clicked.connect(
            self.compare_json_shape
        )

        self.bt_validate_json = QPushButton(
            "Validar JSON"
        )

        self.bt_validate_json.setEnabled(
            False
        )

        self.bt_validate_json.clicked.connect(
            self.validate_json
        )

        self.bt_validate_sicar = QPushButton(
            "Validar SICAR"
        )

        self.bt_validate_sicar.setEnabled(
            False
        )

        self.bt_validate_sicar.clicked.connect(
            self.validate_sicar
        )

        self.bt_export_layers = QPushButton(
            "Exportar Camadas"
        )

        self.bt_export_layers.setEnabled(
            False
        )

        self.bt_export_layers.clicked.connect(
            self.export_json_layers
        )

        self.bt_fix = QPushButton(
            "Corrigir Shape"
        )

        self.bt_fix.setEnabled(
            False
        )

        self.bt_fix.clicked.connect(
            self.fix_shapefile
        )

        self.bt_report_shape = QPushButton(
            "Relatório Shape"
        )

        self.bt_report_shape.setEnabled(
            False
        )

        self.bt_report_shape.clicked.connect(
            self.export_shapefile_report
        )

        self.bt_report_json = QPushButton(
            "Relatório JSON"
        )

        self.bt_report_json.setEnabled(
            False
        )

        self.bt_report_json.clicked.connect(
            self.export_json_report
        )

        self.bt_report_sicar = QPushButton(
            "Relatório SICAR"
        )

        self.bt_report_sicar.setEnabled(
            False
        )

        self.bt_report_sicar.clicked.connect(
            self.export_sicar_report
        )

        self.bt_report_compare = QPushButton(
            "Relatório Comparação"
        )

        self.bt_report_compare.setEnabled(
            False
        )

        self.bt_report_compare.clicked.connect(
            self.export_compare_report
        )

        self.bt_clear = QPushButton(
            "Limpar"
        )

        self.bt_clear.setEnabled(
            False
        )

        self.bt_clear.clicked.connect(
            self.clear_results
        )

        botoes1.addWidget(
            self.bt_import_shape
        )

        botoes1.addWidget(
            self.bt_import_json
        )

        botoes1.addWidget(
            self.cmb_layers
        )

        botoes1.addWidget(
            self.bt_compare
        )

        botoes1.addWidget(
            self.bt_validate_json
        )

        botoes1.addWidget(
            self.bt_validate_sicar
        )

        botoes1.addWidget(
            self.bt_export_layers
        )

        botoes2.addWidget(
            self.bt_fix
        )

        botoes2.addWidget(
            self.bt_report_shape
        )

        botoes2.addWidget(
            self.bt_report_json
        )

        botoes2.addWidget(
            self.bt_report_sicar
        )

        botoes2.addWidget(
            self.bt_report_compare
        )

        botoes2.addWidget(
            self.bt_clear
        )

        self.fields = [

            "Arquivo",
            "Componentes",
            "Arquivos ausentes",
            "CRS",
            "CRS cálculo",
            "Feições",
            "Tipos",
            "Área (ha)",
            "Perímetro (m)",
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
            [
                "Campo",
                "Valor",
            ]
        )

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        for row, field in enumerate(
            self.fields
        ):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    field
                ),
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    "-"
                ),
            )

        self.lbl_json = QLabel(
            "JSON: Nenhum arquivo carregado."
        )

        self.lbl_validation = QLabel()

        self.lbl_sicar = QLabel()

        self.lbl_compare = QLabel()

        self.lbl_status = QLabel(
            "Status: Aguardando."
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            subtitulo
        )

        layout.addLayout(
            botoes1
        )

        layout.addLayout(
            botoes2
        )

        layout.addWidget(
            self.table
        )

        layout.addWidget(
            self.lbl_json
        )

        layout.addWidget(
            self.lbl_validation
        )

        layout.addWidget(
            self.lbl_sicar
        )

        layout.addWidget(
            self.lbl_compare
        )

        layout.addWidget(
            self.lbl_status
        )

        self.setCentralWidget(
            central
        )
        
    def import_shapefile(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Shapefile",
            "",
            "Shapefile (*.shp)",
        )

        if not filename:
            return

        try:

            result = ShapefileController.load(
                filename
            )

            self.state.shapefile_path = result["path"]
            self.state.shapefile_gdf = result["gdf"]
            self.state.shapefile_data = result

            self.update_table(result)

            self.bt_fix.setEnabled(
                result["validation"]["invalid_count"] > 0
            )

            self.bt_report_shape.setEnabled(True)

            self.bt_clear.setEnabled(True)

            if self.state.can_compare:
                self.bt_compare.setEnabled(True)

            self.lbl_status.setText(
                f"Shape carregado: {os.path.basename(filename)}"
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro),
            )


    def import_json(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar JSON",
            "",
            "JSON (*.json)",
        )

        if not filename:
            return

        try:

            result = JsonController.load(
                filename
            )

            self.state.json_path = result["path"]
            self.state.json_data = result["data"]
            self.state.json_layers = result["layers"]
            self.state.json_summary = result["summary"]

            self.cmb_layers.clear()

            self.cmb_layers.addItem(
                "Selecione uma camada..."
            )

            for layer in ComparisonController.available_layers(
                self.state.json_layers
            ):

                self.cmb_layers.addItem(
                    layer
                )

            self.cmb_layers.setEnabled(True)

            self.bt_validate_json.setEnabled(True)
            self.bt_validate_sicar.setEnabled(True)
            self.bt_export_layers.setEnabled(True)
            self.bt_clear.setEnabled(True)

            if self.state.can_compare:
                self.bt_compare.setEnabled(True)

            resumo = self.state.json_summary

            self.lbl_json.setText(

                f"JSON: {os.path.basename(filename)} | "

                f"Camadas: {len(self.state.json_layers)} | "

                f"Geometrias: {resumo['geometry_count']}"

            )

            self.lbl_status.setText(
                "JSON carregado."
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro),
            )


    def compare_json_shape(self):

        if not self.state.can_compare:

            QMessageBox.warning(
                self,
                "Comparação",
                "Carregue um Shape e um JSON.",
            )

            return

        if self.cmb_layers.currentIndex() == 0:

            QMessageBox.warning(
                self,
                "Comparação",
                "Selecione uma camada.",
            )

            return

        layer = self.cmb_layers.currentText()

        try:

            result = (
                ComparisonController.compare_json_layer_with_shapefile(
                    self.state.json_layers,
                    layer,
                    self.state.shapefile_gdf,
                )
            )

            self.state.comparison_layer_name = layer
            self.state.comparison_result = result

            self.bt_report_compare.setEnabled(
                True
            )

            self.lbl_compare.setText(

                f"Comparação: "

                f"{result['status']} | "

                f"Diferença: "

                f"{result['absolute_area_difference_ha']:.4f} ha"

            )

            QMessageBox.information(

                self,

                "Resultado da Comparação",

                self.format_compare(result),

            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro),
            )


    def validate_json(self):

        if not self.state.has_json:
            return

        validation = (
            JsonController.validate_geometries(
                self.state.json_layers
            )
        )

        self.state.geometry_validation = validation

        self.bt_report_json.setEnabled(
            True
        )

        summary = validation["summary"]

        self.lbl_validation.setText(

            f"Geometrias: "

            f"{summary['overall_result']} | "

            f"Camadas: {summary['layer_count']} | "

            f"Inválidas: {summary['invalid_count']}"

        )


    def validate_sicar(self):

        if not self.state.has_json:
            return

        validation = (
            JsonController.validate_sicar_structure(
                self.state.json_layers
            )
        )

        self.state.sicar_validation = validation

        self.bt_report_sicar.setEnabled(
            True
        )

        self.lbl_sicar.setText(

            f"Estrutura SICAR: "

            f"{'OK' if validation['required_ok'] else 'PENDENTE'}"

        )
        
    def export_json_layers(self):

        if not self.state.has_json:
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar pasta",
        )

        if not folder:
            return

        try:

            exported = Exporter.export_layers_as_shapefiles(
                self.state.json_layers,
                folder,
            )

            gpkg = os.path.join(
                folder,
                "GeoCAR_Tools.gpkg",
            )

            Exporter.export_geopackage(
                self.state.json_layers,
                gpkg,
            )

            QMessageBox.information(

                self,

                "Exportação",

                f"{len(exported)} camadas exportadas.\n\n{gpkg}",

            )

            self.lbl_status.setText(
                "Camadas exportadas."
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro),
            )


    def fix_shapefile(self):

        if not self.state.has_shapefile:
            return

        corrected = (
            ShapefileController.fix(
                self.state.shapefile_path
            )
        )

        output, _ = QFileDialog.getSaveFileName(

            self,

            "Salvar Shape",

            "shape_corrigido.shp",

            "Shapefile (*.shp)",

        )

        if not output:
            return

        if not output.lower().endswith(".shp"):
            output += ".shp"

        corrected.to_file(
            output,
            driver="ESRI Shapefile",
            index=False,
            encoding="utf-8",
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Shape corrigido.",
        )


    def export_shapefile_report(self):

        if not self.state.has_shapefile:
            return

        file, _ = QFileDialog.getSaveFileName(

            self,

            "Salvar relatório",

            "relatorio_shape.txt",

            "Texto (*.txt)",

        )

        if not file:
            return

        ReportExporter.shapefile_report(

            file,

            {

                "arquivo": os.path.basename(
                    self.state.shapefile_path
                ),

                **self.state.shapefile_data[
                    "validation"
                ],

            },

        )

        QMessageBox.information(
            self,
            "Relatório",
            "Relatório salvo."
        )


    def export_json_report(self):

        if not self.state.geometry_validation:
            return

        file, _ = QFileDialog.getSaveFileName(

        self,

        "Salvar relatório",

        "relatorio_json.txt",

        "Texto (*.txt)",

        )

        if not file:
            return

        summary = self.state.json_summary.copy()

        summary["Recibo"] = summary.pop(
            "idPai",
            "-"
        )

        summary["Código do Protocolo"] = summary.pop(
            "codigoProtocolo",
            "-"
        )

        ReportExporter.geometry_report(

            file,

            summary,

        )

        QMessageBox.information(

            self,

            "Relatório",

            "Relatório salvo.",

        )


    def export_sicar_report(self):

        if not self.state.sicar_validation:
            return

        file, _ = QFileDialog.getSaveFileName(

            self,

            "Salvar relatório",

            "relatorio_sicar.txt",

            "Texto (*.txt)",

        )

        if not file:
            return

        ReportExporter.sicar_report(

            file,

            self.state.sicar_validation,

        )

        QMessageBox.information(
            self,
            "Relatório",
            "Relatório salvo."
        )


    def export_compare_report(self):

        if not self.state.has_comparison:
            return

        file, _ = QFileDialog.getSaveFileName(

            self,

            "Salvar relatório",

            "comparacao_json_shape.txt",

            "Texto (*.txt)",

        )

        if not file:
            return

        ReportExporter.comparison_report(

            file,

            self.state.comparison_result,

        )

        QMessageBox.information(
            self,
            "Relatório",
            "Relatório salvo."
        )
        
    def clear_results(self):

        self.state.clear_all()

        self.cmb_layers.clear()

        self.cmb_layers.addItem(
            "Selecione uma camada..."
        )

        self.cmb_layers.setEnabled(
            False
        )

        for row in range(
            len(self.fields)
        ):

            self.table.item(
                row,
                1,
            ).setText("-")

        self.bt_compare.setEnabled(
            False
        )

        self.bt_fix.setEnabled(
            False
        )

        self.bt_validate_json.setEnabled(
            False
        )

        self.bt_validate_sicar.setEnabled(
            False
        )

        self.bt_export_layers.setEnabled(
            False
        )

        self.bt_report_shape.setEnabled(
            False
        )

        self.bt_report_json.setEnabled(
            False
        )

        self.bt_report_sicar.setEnabled(
            False
        )

        self.bt_report_compare.setEnabled(
            False
        )

        self.bt_clear.setEnabled(
            False
        )

        self.lbl_json.setText(
            "JSON: Nenhum arquivo carregado."
        )

        self.lbl_validation.setText(
            ""
        )

        self.lbl_sicar.setText(
            ""
        )

        self.lbl_compare.setText(
            ""
        )

        self.lbl_status.setText(
            "Status: Aguardando."
        )


    def update_table(
        self,
        result,
    ):

        metadata = result["metadata"]

        validation = result["validation"]

        values = [

            os.path.basename(
                result["path"]
            ),

            metadata["components"],

            metadata["missing_components"],

            validation["original_crs"],

            validation["calculation_crs"],

            validation["features"],

            validation["geometry_types"],

            validation["area_ha"],

            validation["perimeter_m"],

            validation["invalid_count"],

            validation["null_count"],

            validation["empty_count"],

            validation["multipart_count"],

            validation["interior_rings_count"],

            validation["duplicate_count"],

            validation["result"],

        ]

        for row, value in enumerate(
            values
        ):

            self.table.item(
                row,
                1,
            ).setText(
                str(value)
            )

        self.table.resizeColumnsToContents()


    def format_compare(
        self,
        result,
    ):

        return f"""
Camada JSON

{result['layer_name']}

--------------------------------------------

Feições JSON:

{result['json_features']}

Feições Shape:

{result['shapefile_features']}

--------------------------------------------

Área JSON:

{result['json_area_ha']:.4f} ha

Área Shape:

{result['shapefile_area_ha']:.4f} ha

--------------------------------------------

Diferença:

{result['absolute_area_difference_ha']:.4f} ha

Diferença (%):

{result['area_difference_percent']:.4f}

--------------------------------------------

Interseção:

{result['intersection_area_ha']:.4f} ha

Cobertura JSON:

{result['intersection_percent_json']:.2f} %

Cobertura Shape:

{result['intersection_percent_shapefile']:.2f} %

--------------------------------------------

Área apenas JSON:

{result['json_difference_area_ha']:.4f} ha

Área apenas Shape:

{result['shapefile_difference_area_ha']:.4f} ha

--------------------------------------------

Resultado

{result['status']}
"""