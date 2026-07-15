"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: json_controller.py
Módulo......: Controller do JSON
Versão......: 4.0
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Centraliza a leitura, conversão, validação e preparação das camadas
    extraídas de arquivos JSON do SICAR.
===============================================================================
"""

from typing import Any

import geopandas as gpd

from app.json_reader import JsonReader
from app.sicar_validator import SICARValidator
from app.validators.geometry_validator import GeometryValidator


class JsonController:
    """
    Controller responsável pelas operações com JSON do SICAR.
    """

    @staticmethod
    def load(path: str) -> dict[str, Any]:
        """
        Carrega o JSON, extrai suas camadas e gera um resumo.
        """

        data = JsonReader.open(path)

        layers = JsonReader.extract_layers(
            data
        )

        summary = JsonReader.summary(
            data
        )

        return {
            "path": path,
            "data": data,
            "layers": layers,
            "summary": summary,
        }

    @staticmethod
    def validate_geometries(
        layers: dict[str, gpd.GeoDataFrame],
    ) -> dict[str, Any]:
        """
        Executa a validação geométrica de todas as camadas.
        """

        results = GeometryValidator.validate_layers(
            layers
        )

        summary = GeometryValidator.summary(
            results
        )

        return {
            "results": results,
            "summary": summary,
        }

    @staticmethod
    def validate_sicar_structure(
        layers: dict[str, gpd.GeoDataFrame],
    ) -> dict[str, Any]:
        """
        Valida a presença e as estatísticas das camadas SICAR.
        """

        return SICARValidator.validate(
            layers
        )

    @staticmethod
    def layer_names(
        layers: dict[str, gpd.GeoDataFrame],
    ) -> list[str]:
        """
        Retorna os nomes das camadas em ordem alfabética.
        """

        return sorted(
            layers.keys()
        )

    @staticmethod
    def get_layer(
        layers: dict[str, gpd.GeoDataFrame],
        layer_name: str,
    ) -> gpd.GeoDataFrame | None:
        """
        Retorna uma camada específica.
        """

        return layers.get(
            layer_name
        )

    @staticmethod
    def layers_summary(
        layers: dict[str, gpd.GeoDataFrame],
    ) -> dict[str, dict[str, Any]]:
        """
        Retorna um resumo individual de cada camada.
        """

        summary = {}

        for layer_name, gdf in layers.items():

            summary[layer_name] = (
                GeometryValidator.validate(
                    gdf
                )
            )

        return summary

    @staticmethod
    def count_features(
        layers: dict[str, gpd.GeoDataFrame],
    ) -> int:
        """
        Conta o total de feições existentes nas camadas.
        """

        return sum(
            len(gdf)
            for gdf in layers.values()
        )

    @staticmethod
    def count_layers(
        layers: dict[str, gpd.GeoDataFrame],
    ) -> int:
        """
        Conta o total de camadas.
        """

        return len(
            layers
        )

    @staticmethod
    def has_layer(
        layers: dict[str, gpd.GeoDataFrame],
        layer_name: str,
    ) -> bool:
        """
        Verifica se determinada camada está presente.
        """

        return layer_name in layers

    @staticmethod
    def compare_layer_with_shapefile(
        json_layers: dict[str, gpd.GeoDataFrame],
        layer_name: str,
        shapefile_gdf: gpd.GeoDataFrame,
    ) -> dict[str, Any]:
        """
        Prepara a comparação entre uma camada JSON e um Shapefile.

        A comparação espacial completa será implementada na V4.1.
        """

        json_gdf = json_layers.get(
            layer_name
        )

        if json_gdf is None:

            raise ValueError(
                f"A camada {layer_name} não foi encontrada no JSON."
            )

        json_report = GeometryValidator.validate(
            json_gdf
        )

        shapefile_report = GeometryValidator.validate(
            shapefile_gdf
        )

        area_difference = abs(
            json_report["area_ha"]
            - shapefile_report["area_ha"]
        )

        return {
            "layer_name": layer_name,
            "json_features": json_report["features"],
            "shapefile_features": shapefile_report["features"],
            "json_area_ha": json_report["area_ha"],
            "shapefile_area_ha": shapefile_report["area_ha"],
            "area_difference_ha": round(
                area_difference,
                4,
            ),
            "json_result": json_report["result"],
            "shapefile_result": shapefile_report["result"],
        }