"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: app_state.py
Módulo......: Estado da Aplicação
Versão......: 4.1
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Armazena os arquivos, dados e resultados atualmente carregados na
    aplicação, incluindo resultados de comparação JSON x Shapefile.
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Any

import geopandas as gpd


@dataclass
class AppState:
    """
    Estado compartilhado do GeoCAR Tools.
    """

    shapefile_path: str | None = None
    shapefile_data: dict[str, Any] | None = None
    shapefile_gdf: gpd.GeoDataFrame | None = None

    json_path: str | None = None
    json_data: Any = None
    json_layers: dict[str, gpd.GeoDataFrame] = field(
        default_factory=dict
    )
    json_summary: dict[str, Any] | None = None

    geometry_validation: dict[str, Any] = field(
        default_factory=dict
    )
    sicar_validation: dict[str, Any] | None = None

    comparison_layer_name: str | None = None
    comparison_result: dict[str, Any] | None = None

    def clear_shapefile(self) -> None:
        """
        Remove do estado todos os dados do Shapefile.
        """

        self.shapefile_path = None
        self.shapefile_data = None
        self.shapefile_gdf = None

        self.clear_comparison()

    def clear_json(self) -> None:
        """
        Remove do estado todos os dados do JSON.
        """

        self.json_path = None
        self.json_data = None
        self.json_layers.clear()
        self.json_summary = None
        self.geometry_validation.clear()
        self.sicar_validation = None

        self.clear_comparison()

    def clear_comparison(self) -> None:
        """
        Limpa o resultado da comparação atual.
        """

        self.comparison_layer_name = None
        self.comparison_result = None

    def clear_all(self) -> None:
        """
        Limpa completamente o estado da aplicação.
        """

        self.clear_shapefile()
        self.clear_json()
        self.clear_comparison()

    @property
    def has_shapefile(self) -> bool:
        """
        Indica se existe um Shapefile carregado.
        """

        return (
            self.shapefile_path is not None
            and self.shapefile_data is not None
            and self.shapefile_gdf is not None
            and not self.shapefile_gdf.empty
        )

    @property
    def has_json(self) -> bool:
        """
        Indica se existe um JSON com camadas carregadas.
        """

        return (
            self.json_path is not None
            and bool(self.json_layers)
        )

    @property
    def has_comparison(self) -> bool:
        """
        Indica se existe um resultado de comparação.
        """

        return (
            self.comparison_layer_name is not None
            and self.comparison_result is not None
        )

    @property
    def can_compare(self) -> bool:
        """
        Indica se JSON e Shapefile estão disponíveis para comparação.
        """

        return (
            self.has_shapefile
            and self.has_json
        )