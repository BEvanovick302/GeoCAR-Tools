"""
===============================================================================
GeoCAR Tools
Versão 2.6
Geração de relatório das camadas JSON
===============================================================================
"""

import os
from datetime import datetime


class JsonReporter:

    @staticmethod
    def export_report(
        json_filename,
        validation_results,
        validation_summary,
        output_path,
    ):

        if not validation_results:
            raise Exception(
                "A validação do JSON ainda não foi executada."
            )

        if not output_path.lower().endswith(".txt"):
            output_path += ".txt"

        output_directory = (
            os.path.dirname(output_path)
            or "."
        )

        os.makedirs(
            output_directory,
            exist_ok=True,
        )

        lines = [
            "GeoCAR Tools",
            "Relatório de Validação do JSON",
            "=" * 60,
            "",
            f"Arquivo: {os.path.basename(json_filename)}",
            f"Caminho: {json_filename}",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "",
            "RESUMO GERAL",
            "-" * 60,
            f"Resultado: {validation_summary['overall_result']}",
            f"Camadas: {validation_summary['layer_count']}",
            f"Feições: {validation_summary['feature_count']}",
            f"Camadas aprovadas: {validation_summary['approved_layers']}",
            (
                "Camadas que requerem atenção: "
                f"{validation_summary['attention_layers']}"
            ),
            f"Geometrias inválidas: {validation_summary['invalid_count']}",
            f"Geometrias nulas: {validation_summary['null_count']}",
            f"Geometrias vazias: {validation_summary['empty_count']}",
            f"Geometrias duplicadas: {validation_summary['duplicate_count']}",
            "",
            "DETALHAMENTO POR CAMADA",
            "=" * 60,
        ]

        for layer_name, result in validation_results.items():

            lines.extend(
                [
                    "",
                    f"Camada: {layer_name}",
                    "-" * 60,
                    f"Resultado: {result['result']}",
                    f"Feições: {result['features']}",
                    f"Tipos de geometria: {result['geometry_types']}",
                    f"Geometrias inválidas: {result['invalid_count']}",
                    f"Geometrias nulas: {result['null_count']}",
                    f"Geometrias vazias: {result['empty_count']}",
                    f"Geometrias multipartes: {result['multipart_count']}",
                    f"Geometrias duplicadas: {result['duplicate_count']}",
                ]
            )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write("\n".join(lines))

        return output_path