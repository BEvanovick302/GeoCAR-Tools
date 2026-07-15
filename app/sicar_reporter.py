"""
===============================================================================
GeoCAR Tools
Versão 3.1
Relatório da validação estrutural do SICAR
===============================================================================
"""

import os
from datetime import datetime


class SICARReporter:

    @staticmethod
    def export_report(
        json_filename,
        validation,
        output_path,
    ):

        if not validation:
            raise Exception(
                "A validação da estrutura SICAR ainda não foi executada."
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

        result = (
            "Aprovado"
            if validation["required_ok"]
            else "Requer atenção"
        )

        missing_layers = (
            ", ".join(validation["missing_layers"])
            if validation["missing_layers"]
            else "Nenhuma"
        )

        lines = [
            "GeoCAR Tools",
            "Relatório de Validação da Estrutura SICAR",
            "=" * 65,
            "",
            f"Arquivo JSON: {os.path.basename(json_filename)}",
            f"Caminho: {json_filename}",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "",
            "RESUMO",
            "-" * 65,
            f"Resultado: {result}",
            f"Quantidade de camadas: {validation['layer_count']}",
            f"Camadas obrigatórias presentes: "
            f"{'Sim' if validation['required_ok'] else 'Não'}",
            f"Camadas ausentes: {missing_layers}",
            "",
            "CAMADAS ENCONTRADAS",
            "-" * 65,
        ]

        for layer_name in validation["existing_layers"]:
            lines.append(
                f"• {layer_name}"
            )

        lines.extend(
            [
                "",
                "ÁREAS POR CAMADA",
                "-" * 65,
            ]
        )

        for layer_name, area in validation["areas"].items():
            lines.append(
                f"• {layer_name}: {area:.2f} ha"
            )

        lines.extend(
            [
                "",
                "FEIÇÕES POR CAMADA",
                "-" * 65,
            ]
        )

        for layer_name, feature_count in (
            validation["features"].items()
        ):
            lines.append(
                f"• {layer_name}: {feature_count}"
            )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(
                "\n".join(lines)
            )

        return output_path