"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: comparison_controller.py
Módulo......: Controller de Comparação
Versão......: 4.1
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Centraliza a comparação entre uma camada do JSON do SICAR e um
    Shapefile carregado na aplicação.
===============================================================================
"""

from __future__ import annotations

from typing import Any

import geopandas as gpd

from app.services.comparison_service import ComparisonService


class ComparisonController:
    """
    Controller responsável pelas comparações espaciais.
    """

    @staticmethod
    def compare_json_layer_with_shapefile(
        json_layers: dict[str, gpd.GeoDataFrame],
        layer_name: str,
        shapefile_gdf: gpd.GeoDataFrame,
    ) -> dict[str, Any]:
        """
        Compara uma camada JSON específica com o Shapefile carregado.
        """

        if not json_layers:
            raise ValueError(
                "Nenhuma camada JSON está disponível."
            )

        if not layer_name:
            raise ValueError(
                "Selecione uma camada JSON."
            )

        json_gdf = json_layers.get(
            layer_name
        )

        if json_gdf is None:
            raise ValueError(
                f"A camada {layer_name} não foi encontrada."
            )

        if shapefile_gdf is None:
            raise ValueError(
                "Nenhum Shapefile está carregado."
            )

        result = ComparisonService.compare(
            json_gdf=json_gdf,
            shapefile_gdf=shapefile_gdf,
        )

        result["layer_name"] = layer_name

        return result

    @staticmethod
    def available_layers(
        json_layers: dict[str, gpd.GeoDataFrame],
    ) -> list[str]:
        """
        Retorna as camadas disponíveis para comparação.
        """

        return sorted(
            json_layers.keys()
        )

    @staticmethod
    def can_compare(
        json_layers: dict[str, gpd.GeoDataFrame],
        shapefile_gdf: gpd.GeoDataFrame | None,
    ) -> bool:
        """
        Verifica se há dados suficientes para realizar a comparação.
        """

        return (
            bool(json_layers)
            and shapefile_gdf is not None
            and not shapefile_gdf.empty
        )