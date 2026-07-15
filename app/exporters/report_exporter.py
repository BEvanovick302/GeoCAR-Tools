"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: report_exporter.py
Módulo......: Exportador de Relatórios
Versão......: 4.0
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Responsável por exportar relatórios da aplicação.
===============================================================================
"""

from __future__ import annotations

import os
from datetime import datetime


class ReportExporter:

    TITLE = (
        "GeoCAR Tools - Relatório Técnico"
    )

    @staticmethod
    def export_txt(
        output_path: str,
        title: str,
        sections: list[tuple[str, dict]],
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

            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",

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
        output_path,
        data,
    ):

        return ReportExporter.export_txt(

            output_path,

            "Relatório do Shapefile",

            [

                (

                    "Informações",

                    {

                        "Arquivo":
                            data.get("arquivo"),

                        "Feições":
                            data.get("features"),

                        "Área (ha)":
                            data.get("area_ha"),

                        "Perímetro (m)":
                            data.get("perimeter_m"),

                        "CRS":
                            data.get("crs"),

                        "Resultado":
                            data.get("result"),

                    },

                ),

            ],

        )

    @staticmethod
    def geometry_report(
        output_path,
        summary,
    ):

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
        output_path,
        validation,
    ):

        return ReportExporter.export_txt(

            output_path,

            "Estrutura SICAR",

            [

                (

                    "Resumo",

                    {

                        "Resultado":

                            (
                                "Aprovado"

                                if validation["required_ok"]

                                else "Requer atenção"

                            ),

                        "Quantidade de camadas":

                            validation["layer_count"],

                        "Camadas ausentes":

                            ", ".join(
                                validation["missing_layers"]
                            )

                            if validation["missing_layers"]

                            else "Nenhuma",

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
        output_path,
        comparison,
    ):

        return ReportExporter.export_txt(

            output_path,

            "Comparação",

            [

                (

                    "Resultado",

                    comparison,

                ),

            ],

        )