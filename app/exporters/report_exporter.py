"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: report_exporter.py
Módulo......: Exportador de Relatórios
Versão......: 4.1
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Exporta relatórios técnicos do Shapefile, JSON, estrutura SICAR
    e comparação JSON x Shapefile.
===============================================================================
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any


class ReportExporter:

    TITLE = "GeoCAR Tools - Relatório Técnico"

    @staticmethod
    def export_txt(
        output_path: str,
        title: str,
        sections: list[tuple[str, dict[str, Any]]],
    ) -> str:

        if not output_path.lower().endswith(".txt"):
            output_path += ".txt"

        directory = (
            os.path.dirname(output_path)
            or "."
        )

        os.makedirs(
            directory,
            exist_ok=True,
        )

        lines = [
            ReportExporter.TITLE,
            "=" * 70,
            "",
            f"Tipo: {title}",
            (
                "Data: "
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            ),
            "",
        ]

        for section_name, values in sections:

            lines.append(
                section_name.upper()
            )

            lines.append(
                "-" * 70
            )

            for key, value in values.items():

                lines.append(
                    f"{key}: {value}"
                )

            lines.append("")

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "\n".join(lines)
            )

        return output_path

    @staticmethod
    def shapefile_report(
        output_path: str,
        data: dict[str, Any],
    ) -> str:

        return ReportExporter.export_txt(
            output_path,
            "Relatório do Shapefile",
            [
                (
                    "Informações",
                    {
                        "Arquivo": data.get(
                            "arquivo"
                        ),
                        "Feições": data.get(
                            "features"
                        ),
                        "Área (ha)": data.get(
                            "area_ha"
                        ),
                        "Perímetro (m)": data.get(
                            "perimeter_m"
                        ),
                        "CRS": data.get(
                            "crs"
                        ),
                        "Resultado": data.get(
                            "result"
                        ),
                    },
                ),
            ],
        )

    @staticmethod
    def geometry_report(
        output_path: str,
        summary: dict[str, Any],
    ) -> str:

        return ReportExporter.export_txt(
            output_path,
            "Validação Geométrica",
            [
                (
                    "Resumo",
                    summary,
                ),
            ],
        )

    @staticmethod
    def sicar_report(
        output_path: str,
        validation: dict[str, Any],
    ) -> str:

        return ReportExporter.export_txt(
            output_path,
            "Estrutura SICAR",
            [
                (
                    "Resumo",
                    {
                        "Resultado": (
                            "Aprovado"
                            if validation["required_ok"]
                            else "Requer atenção"
                        ),
                        "Quantidade de camadas": (
                            validation["layer_count"]
                        ),
                        "Camadas ausentes": (
                            ", ".join(
                                validation["missing_layers"]
                            )
                            if validation["missing_layers"]
                            else "Nenhuma"
                        ),
                    },
                ),
                (
                    "Áreas",
                    validation["areas"],
                ),
                (
                    "Feições",
                    validation["features"],
                ),
            ],
        )

    @staticmethod
    def comparison_report(
        output_path: str,
        comparison: dict[str, Any],
    ) -> str:

        return ReportExporter.export_txt(
            output_path,
            "Comparação JSON x Shapefile",
            [
                (
                    "Identificação",
                    {
                        "Camada JSON": comparison.get(
                            "layer_name"
                        ),
                        "CRS de cálculo": comparison.get(
                            "calculation_crs"
                        ),
                        "Status": comparison.get(
                            "status"
                        ),
                    },
                ),
                (
                    "Quantidades",
                    {
                        "Feições JSON": comparison.get(
                            "json_features"
                        ),
                        "Feições Shapefile": comparison.get(
                            "shapefile_features"
                        ),
                    },
                ),
                (
                    "Áreas",
                    {
                        "Área JSON (ha)": comparison.get(
                            "json_area_ha"
                        ),
                        "Área Shapefile (ha)": comparison.get(
                            "shapefile_area_ha"
                        ),
                        "Diferença absoluta (ha)": comparison.get(
                            "absolute_area_difference_ha"
                        ),
                        "Diferença percentual (%)": comparison.get(
                            "area_difference_percent"
                        ),
                    },
                ),
                (
                    "Interseção",
                    {
                        "Área de interseção (ha)": comparison.get(
                            "intersection_area_ha"
                        ),
                        (
                            "Cobertura sobre o JSON (%)"
                        ): comparison.get(
                            "intersection_percent_json"
                        ),
                        (
                            "Cobertura sobre o Shapefile (%)"
                        ): comparison.get(
                            "intersection_percent_shapefile"
                        ),
                    },
                ),
                (
                    "Diferenças espaciais",
                    {
                        (
                            "Área apenas no JSON (ha)"
                        ): comparison.get(
                            "json_difference_area_ha"
                        ),
                        (
                            "Área apenas no Shapefile (ha)"
                        ): comparison.get(
                            "shapefile_difference_area_ha"
                        ),
                    },
                ),
            ],
        )