"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: main_window.py
Módulo......: Interface Principal
Versão......: 4.0
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Janela principal do GeoCAR Tools integrada ao estado, controllers,
    serviços e exportadores da aplicação.
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

from app.controllers.json_controller import JsonController
from app.controllers.shapefile_controller import ShapefileController
from app.core.app_state import AppState
from app.exporter import Exporter
from app.exporters.report_exporter import ReportExporter


class MainWindow(QMainWindow):
    """
    Janela principal do GeoCAR Tools.
    """

    def __init__(
        self,
        state: AppState,
    ):
        super().__init__()

        self.state = state

        self.setWindowTitle(
            "GeoCAR Tools - V4.0"
        )
        self.resize(1380, 940)
        self.setMinimumSize(1100, 740)

        self._create_ui()

    def _create_ui(self) -> None:
        """
        Cria os componentes da interface.
        """

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel(
            "🌎 GeoCAR Tools"
        )
        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        title.setStyleSheet(
            """
            font-size: 26px;
            font-weight: bold;
            padding: 10px;
            """
        )

        subtitle = QLabel(
            "Análise de Shapefile e JSON do SICAR"
        )
        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        first_button_row = QHBoxLayout()
        second_button_row = QHBoxLayout()

        self.button_import_shape = QPushButton(
            "Importar Shapefile"
        )
        self.button_import_shape.clicked.connect(
            self.import_shapefile
        )

        self.button_import_json = QPushButton(
            "Importar JSON SICAR"
        )
        self.button_import_json.clicked.connect(
            self.import_json
        )

        self.button_validate_json = QPushButton(
            "Validar Geometrias JSON"
        )
        self.button_validate_json.setEnabled(
            False
        )
        self.button_validate_json.clicked.connect(
            self.validate_json
        )

        self.button_validate_sicar = QPushButton(
            "Validar Estrutura SICAR"
        )
        self.button_validate_sicar.setEnabled(
            False
        )
        self.button_validate_sicar.clicked.connect(
            self.validate_sicar
        )

        self.button_export_layers = QPushButton(
            "Exportar Camadas SICAR"
        )
        self.button_export_layers.setEnabled(
            False
        )
        self.button_export_layers.clicked.connect(
            self.export_json_layers
        )

        self.button_fix_shape = QPushButton(
            "Corrigir Shapefile"
        )
        self.button_fix_shape.setEnabled(
            False
        )
        self.button_fix_shape.clicked.connect(
            self.fix_shapefile
        )

        self.button_shape_report = QPushButton(
            "Relatório Shapefile"
        )
        self.button_shape_report.setEnabled(
            False
        )
        self.button_shape_report.clicked.connect(
            self.export_shapefile_report
        )

        self.button_json_report = QPushButton(
            "Relatório Geométrico JSON"
        )
        self.button_json_report.setEnabled(
            False
        )
        self.button_json_report.clicked.connect(
            self.export_json_report
        )

        self.button_sicar_report = QPushButton(
            "Relatório Estrutura SICAR"
        )
        self.button_sicar_report.setEnabled(
            False
        )
        self.button_sicar_report.clicked.connect(
            self.export_sicar_report
        )

        self.button_clear = QPushButton(
            "Limpar"
        )
        self.button_clear.setEnabled(
            False
        )
        self.button_clear.clicked.connect(
            self.clear_results
        )

        first_button_row.addWidget(
            self.button_import_shape
        )
        first_button_row.addWidget(
            self.button_import_json
        )
        first_button_row.addWidget(
            self.button_validate_json
        )
        first_button_row.addWidget(
            self.button_validate_sicar
        )
        first_button_row.addWidget(
            self.button_export_layers
        )

        second_button_row.addWidget(
            self.button_fix_shape
        )
        second_button_row.addWidget(
            self.button_shape_report
        )
        second_button_row.addWidget(
            self.button_json_report
        )
        second_button_row.addWidget(
            self.button_sicar_report
        )
        second_button_row.addWidget(
            self.button_clear
        )

        self.fields = [
            "Arquivo",
            "Componentes",
            "Arquivos ausentes",
            "CRS original",
            "CRS cálculo",
            "Feições",
            "Tipos geométricos",
            "Área (ha)",
            "Perímetro (m)",
            "Inválidas",
            "Nulas",
            "Vazias",
            "Multipartes",
            "Buracos internos",
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
        self.table.verticalHeader().setVisible(
            False
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(
            True
        )

        for row, field in enumerate(
            self.fields
        ):
            self.table.setItem(
                row,
                0,
                QTableWidgetItem(field),
            )
            self.table.setItem(
                row,
                1,
                QTableWidgetItem("-"),
            )

        self.table.resizeColumnsToContents()

        self.lbl_json = QLabel(
            "JSON SICAR: nenhum arquivo carregado."
        )
        self.lbl_json.setWordWrap(
            True
        )

        self.lbl_json_validation = QLabel(
            "Validação geométrica do JSON: não executada."
        )
        self.lbl_json_validation.setWordWrap(
            True
        )

        self.lbl_sicar_validation = QLabel(
            "Validação da estrutura SICAR: não executada."
        )
        self.lbl_sicar_validation.setWordWrap(
            True
        )

        self.lbl_status = QLabel(
            "Status: aguardando seleção."
        )
        self.lbl_status.setWordWrap(
            True
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(first_button_row)
        layout.addLayout(second_button_row)
        layout.addWidget(self.table)
        layout.addWidget(self.lbl_json)
        layout.addWidget(
            self.lbl_json_validation
        )
        layout.addWidget(
            self.lbl_sicar_validation
        )
        layout.addWidget(self.lbl_status)

        self.setCentralWidget(central)
        
    def import_shapefile(self) -> None:
        """
        Importa e analisa um Shapefile.
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Shapefile",
            "",
            "Shapefile (*.shp)",
        )

        if not file_path:
            self.lbl_status.setText(
                "Status: importação cancelada."
            )
            return

        try:
            result = ShapefileController.load(
                file_path
            )

            self.state.shapefile_path = result[
                "path"
            ]
            self.state.shapefile_gdf = result[
                "gdf"
            ]
            self.state.shapefile_data = result

            self._update_shapefile_table(
                result
            )

            invalid_count = result[
                "validation"
            ]["invalid_count"]

            self.button_fix_shape.setEnabled(
                invalid_count > 0
            )
            self.button_shape_report.setEnabled(
                True
            )
            self.button_clear.setEnabled(
                True
            )

            self.lbl_status.setText(
                "Status: Shapefile carregado "
                f"com sucesso: {os.path.basename(file_path)}"
            )

        except Exception as error:
            self.state.clear_shapefile()

            self.button_fix_shape.setEnabled(
                False
            )
            self.button_shape_report.setEnabled(
                False
            )

            QMessageBox.critical(
                self,
                "Erro ao importar Shapefile",
                str(error),
            )

            self.lbl_status.setText(
                "Status: erro ao importar Shapefile."
            )

    def import_json(self) -> None:
        """
        Importa o JSON do SICAR e extrai suas camadas.
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar JSON do SICAR",
            "",
            "Arquivo JSON (*.json)",
        )

        if not file_path:
            self.lbl_status.setText(
                "Status: importação cancelada."
            )
            return

        try:
            result = JsonController.load(
                file_path
            )

            self.state.json_path = result[
                "path"
            ]
            self.state.json_data = result[
                "data"
            ]
            self.state.json_layers = result[
                "layers"
            ]
            self.state.json_summary = result[
                "summary"
            ]

            self.state.geometry_validation.clear()
            self.state.sicar_validation = None

            layer_names = JsonController.layer_names(
                self.state.json_layers
            )

            summary = self.state.json_summary

            self.lbl_json.setText(
                f"JSON SICAR: {os.path.basename(file_path)} | "
                f"Camadas: {len(layer_names)} | "
                f"Geometrias: {summary['geometry_count']} | "
                f"{', '.join(layer_names)}"
            )

            self.lbl_json_validation.setText(
                "Validação geométrica do JSON: "
                "não executada."
            )

            self.lbl_sicar_validation.setText(
                "Validação da estrutura SICAR: "
                "não executada."
            )

            has_layers = bool(
                self.state.json_layers
            )

            self.button_validate_json.setEnabled(
                has_layers
            )
            self.button_validate_sicar.setEnabled(
                has_layers
            )
            self.button_export_layers.setEnabled(
                has_layers
            )
            self.button_json_report.setEnabled(
                False
            )
            self.button_sicar_report.setEnabled(
                False
            )
            self.button_clear.setEnabled(
                True
            )

            QMessageBox.information(
                self,
                "JSON SICAR carregado",
                (
                    f"Arquivo: {os.path.basename(file_path)}\n\n"
                    f"Camadas: {len(layer_names)}\n"
                    f"Geometrias: {summary['geometry_count']}\n"
                    f"Polígonos: {summary['polygon_count']}\n"
                    f"Multipolígonos: "
                    f"{summary['multipolygon_count']}\n"
                    f"Pontos: {summary['point_count']}\n"
                    f"Linhas: {summary['line_count']}\n\n"
                    f"{self._format_layers(layer_names)}"
                ),
            )

            self.lbl_status.setText(
                "Status: JSON SICAR carregado "
                f"com sucesso: {os.path.basename(file_path)}"
            )

        except Exception as error:
            self.state.clear_json()

            self.button_validate_json.setEnabled(
                False
            )
            self.button_validate_sicar.setEnabled(
                False
            )
            self.button_export_layers.setEnabled(
                False
            )
            self.button_json_report.setEnabled(
                False
            )
            self.button_sicar_report.setEnabled(
                False
            )

            QMessageBox.critical(
                self,
                "Erro ao importar JSON",
                str(error),
            )

            self.lbl_status.setText(
                "Status: erro ao importar JSON."
            )

    def validate_json(self) -> None:
        """
        Valida as geometrias das camadas JSON.
        """

        if not self.state.has_json:
            return

        try:
            validation = (
                JsonController.validate_geometries(
                    self.state.json_layers
                )
            )

            self.state.geometry_validation = (
                validation
            )

            results = validation["results"]
            summary = validation["summary"]

            self.button_json_report.setEnabled(
                True
            )

            self.lbl_json_validation.setText(
                "Validação geométrica do JSON: "
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
                "Validação geométrica",
                self._format_geometry_validation(
                    results,
                    summary,
                ),
            )

            self.lbl_status.setText(
                "Status: validação geométrica "
                "do JSON concluída."
            )

        except Exception as error:
            self.state.geometry_validation.clear()

            self.button_json_report.setEnabled(
                False
            )

            QMessageBox.critical(
                self,
                "Erro na validação geométrica",
                str(error),
            )

            self.lbl_status.setText(
                "Status: erro na validação "
                "geométrica do JSON."
            )

    def validate_sicar(self) -> None:
        """
        Valida a estrutura de camadas do SICAR.
        """

        if not self.state.has_json:
            return

        try:
            validation = (
                JsonController.validate_sicar_structure(
                    self.state.json_layers
                )
            )

            self.state.sicar_validation = (
                validation
            )

            missing_layers = validation[
                "missing_layers"
            ]

            missing_text = (
                ", ".join(missing_layers)
                if missing_layers
                else "Nenhuma"
            )

            result_text = (
                "Aprovado"
                if validation["required_ok"]
                else "Requer atenção"
            )

            self.lbl_sicar_validation.setText(
                "Validação da estrutura SICAR: "
                f"{result_text} | "
                f"Camadas: {validation['layer_count']} | "
                f"Ausentes: {missing_text}"
            )

            self.button_sicar_report.setEnabled(
                True
            )

            QMessageBox.information(
                self,
                "Validação da estrutura SICAR",
                self._format_sicar_validation(
                    validation
                ),
            )

            self.lbl_status.setText(
                "Status: validação da estrutura "
                "SICAR concluída."
            )

        except Exception as error:
            self.state.sicar_validation = None

            self.button_sicar_report.setEnabled(
                False
            )

            QMessageBox.critical(
                self,
                "Erro na validação SICAR",
                str(error),
            )

            self.lbl_status.setText(
                "Status: erro na validação "
                "da estrutura SICAR."
            )
            
    def export_json_layers(self) -> None:
        """
        Exporta as camadas do JSON para Shapefile e GeoPackage.
        """

        if not self.state.has_json:
            return

        output_directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar pasta de saída",
        )

        if not output_directory:
            return

        try:
            exported_files = (
                Exporter.export_layers_as_shapefiles(
                    self.state.json_layers,
                    output_directory,
                )
            )

            geopackage_path = os.path.join(
                output_directory,
                "GeoCAR_Tools_SICAR.gpkg",
            )

            Exporter.export_geopackage(
                self.state.json_layers,
                geopackage_path,
            )

            QMessageBox.information(
                self,
                "Exportação concluída",
                (
                    f"{len(exported_files)} arquivo(s) "
                    "Shapefile exportado(s).\n\n"
                    f"GeoPackage:\n{geopackage_path}"
                ),
            )

            self.lbl_status.setText(
                "Status: camadas do JSON exportadas."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro na exportação",
                str(error),
            )

            self.lbl_status.setText(
                "Status: erro ao exportar camadas."
            )

    def fix_shapefile(self) -> None:
        """
        Corrige geometrias inválidas e salva um novo Shapefile.
        """

        if not self.state.has_shapefile:
            return

        corrected_gdf = ShapefileController.fix(
            self.state.shapefile_path
        )

        original_name = os.path.splitext(
            os.path.basename(
                self.state.shapefile_path
            )
        )[0]

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Shapefile corrigido",
            f"{original_name}_corrigido.shp",
            "Shapefile (*.shp)",
        )

        if not output_path:
            return

        if not output_path.lower().endswith(".shp"):
            output_path += ".shp"

        try:
            corrected_gdf.to_file(
                output_path,
                driver="ESRI Shapefile",
                encoding="utf-8",
                index=False,
            )

            result = ShapefileController.load(
                output_path
            )

            self.state.shapefile_path = result[
                "path"
            ]
            self.state.shapefile_gdf = result[
                "gdf"
            ]
            self.state.shapefile_data = result

            self._update_shapefile_table(
                result
            )

            self.button_fix_shape.setEnabled(
                result["validation"][
                    "invalid_count"
                ] > 0
            )

            QMessageBox.information(
                self,
                "Correção concluída",
                "Shapefile corrigido e salvo.",
            )

            self.lbl_status.setText(
                f"Status: arquivo corrigido salvo em {output_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro ao salvar correção",
                str(error),
            )

            self.lbl_status.setText(
                "Status: erro ao salvar correção."
            )

    def export_shapefile_report(self) -> None:
        """
        Exporta o relatório do Shapefile.
        """

        if not self.state.has_shapefile:
            return

        file_name = os.path.splitext(
            os.path.basename(
                self.state.shapefile_path
            )
        )[0]

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatório do Shapefile",
            f"relatorio_{file_name}.txt",
            "Arquivo de texto (*.txt)",
        )

        if not output_path:
            return

        validation = self.state.shapefile_data[
            "validation"
        ]

        report_data = {
            "arquivo": os.path.basename(
                self.state.shapefile_path
            ),
            "features": validation["features"],
            "area_ha": validation["area_ha"],
            "perimeter_m": validation[
                "perimeter_m"
            ],
            "crs": validation["original_crs"],
            "result": validation["result"],
        }

        try:
            saved_path = (
                ReportExporter.shapefile_report(
                    output_path,
                    report_data,
                )
            )

            QMessageBox.information(
                self,
                "Relatório exportado",
                f"Relatório salvo em:\n{saved_path}",
            )

            self.lbl_status.setText(
                f"Status: relatório salvo em {saved_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro ao exportar relatório",
                str(error),
            )

    def export_json_report(self) -> None:
        """
        Exporta o relatório geométrico das camadas JSON.
        """

        validation = (
            self.state.geometry_validation
        )

        if not validation:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatório geométrico",
            "relatorio_geometrico_json.txt",
            "Arquivo de texto (*.txt)",
        )

        if not output_path:
            return

        try:
            saved_path = (
                ReportExporter.geometry_report(
                    output_path,
                    validation["summary"],
                )
            )

            QMessageBox.information(
                self,
                "Relatório exportado",
                f"Relatório salvo em:\n{saved_path}",
            )

            self.lbl_status.setText(
                f"Status: relatório salvo em {saved_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro ao exportar relatório",
                str(error),
            )

    def export_sicar_report(self) -> None:
        """
        Exporta o relatório da estrutura SICAR.
        """

        validation = (
            self.state.sicar_validation
        )

        if not validation:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatório da estrutura SICAR",
            "relatorio_estrutura_sicar.txt",
            "Arquivo de texto (*.txt)",
        )

        if not output_path:
            return

        try:
            saved_path = (
                ReportExporter.sicar_report(
                    output_path,
                    validation,
                )
            )

            QMessageBox.information(
                self,
                "Relatório exportado",
                f"Relatório salvo em:\n{saved_path}",
            )

            self.lbl_status.setText(
                f"Status: relatório salvo em {saved_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro ao exportar relatório",
                str(error),
            )

    def clear_results(self) -> None:
        """
        Limpa os dados e restaura a interface.
        """

        self.state.clear_all()

        for row in range(
            len(self.fields)
        ):
            self.table.item(
                row,
                1,
            ).setText("-")

        self.lbl_json.setText(
            "JSON SICAR: nenhum arquivo carregado."
        )

        self.lbl_json_validation.setText(
            "Validação geométrica do JSON: "
            "não executada."
        )

        self.lbl_sicar_validation.setText(
            "Validação da estrutura SICAR: "
            "não executada."
        )

        self.button_validate_json.setEnabled(
            False
        )
        self.button_validate_sicar.setEnabled(
            False
        )
        self.button_export_layers.setEnabled(
            False
        )
        self.button_fix_shape.setEnabled(
            False
        )
        self.button_shape_report.setEnabled(
            False
        )
        self.button_json_report.setEnabled(
            False
        )
        self.button_sicar_report.setEnabled(
            False
        )
        self.button_clear.setEnabled(
            False
        )

        self.lbl_status.setText(
            "Status: resultados limpos."
        )

    def _update_shapefile_table(
        self,
        result: dict,
    ) -> None:
        """
        Atualiza a tabela com os dados do Shapefile.
        """

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

        for row, value in enumerate(values):
            self.table.item(
                row,
                1,
            ).setText(
                str(value)
            )

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(
            True
        )

    def _format_geometry_validation(
        self,
        results: dict,
        summary: dict,
    ) -> str:
        """
        Formata o resultado da validação geométrica.
        """

        lines = [
            f"Resultado geral: {summary['overall_result']}",
            f"Camadas: {summary['layer_count']}",
            f"Feições: {summary['feature_count']}",
            "",
        ]

        for layer_name, result in results.items():
            lines.extend(
                [
                    layer_name,
                    f"  Resultado: {result['result']}",
                    f"  Feições: {result['features']}",
                    (
                        "  Tipos geométricos: "
                        f"{result['geometry_types']}"
                    ),
                    (
                        "  Inválidas: "
                        f"{result['invalid_count']}"
                    ),
                    (
                        "  Multipartes: "
                        f"{result['multipart_count']}"
                    ),
                    "",
                ]
            )

        return "\n".join(lines)

    def _format_sicar_validation(
        self,
        validation: dict,
    ) -> str:
        """
        Formata o resultado da validação estrutural SICAR.
        """

        result_text = (
            "Aprovado"
            if validation["required_ok"]
            else "Requer atenção"
        )

        missing_layers = (
            ", ".join(
                validation["missing_layers"]
            )
            if validation["missing_layers"]
            else "Nenhuma"
        )

        lines = [
            f"Resultado: {result_text}",
            (
                "Camadas encontradas: "
                f"{validation['layer_count']}"
            ),
            f"Camadas ausentes: {missing_layers}",
            "",
            "Áreas por camada:",
        ]

        for layer_name, area in (
            validation["areas"].items()
        ):
            lines.append(
                f"• {layer_name}: {area:.4f} ha"
            )

        return "\n".join(lines)

    @staticmethod
    def _format_layers(
        layers: list[str],
    ) -> str:
        """
        Formata a lista de camadas.
        """

        if not layers:
            return "Nenhuma camada."

        return "\n".join(
            f"• {layer}"
            for layer in layers
        )