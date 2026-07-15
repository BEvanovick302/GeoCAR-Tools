"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: area_service.py
Módulo......: Serviços de Área
Versão......: 4.0.1
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Centraliza cálculos métricos de área e perímetro e trata arquivos
    com CRS ausente ou inválido.
===============================================================================
"""

from __future__ import annotations

import geopandas as gpd
from pyproj import CRS
from pyproj.exceptions import CRSError

from app.services.geometry_service import GeometryService


class AreaService:
    """
    Serviço responsável por cálculos de área e perímetro.
    """

    FALLBACK_GEOGRAPHIC_CRS = "EPSG:4674"

    @staticmethod
    def validate_crs(
        gdf: gpd.GeoDataFrame,
    ) -> CRS:
        """
        Valida e retorna o CRS da camada.
        """

        if gdf.crs is None:
            raise ValueError(
                "A camada não possui CRS definido."
            )

        try:
            return CRS.from_user_input(
                gdf.crs
            )

        except CRSError as error:
            raise ValueError(
                "O Shapefile possui um CRS inválido ou "
                f"não reconhecido: {gdf.crs}. "
                "Corrija o arquivo .prj no QGIS antes de "
                "realizar cálculos de área e perímetro."
            ) from error

    @staticmethod
    def estimate_metric_crs(
        gdf: gpd.GeoDataFrame,
    ) -> CRS:
        """
        Estima um CRS UTM adequado para cálculos métricos.
        """

        AreaService.validate_crs(
            gdf
        )

        try:
            metric_crs = gdf.estimate_utm_crs()

        except CRSError as error:
            raise ValueError(
                "Não foi possível utilizar o CRS informado "
                f"pelo Shapefile: {gdf.crs}."
            ) from error

        if metric_crs is None:
            raise ValueError(
                "Não foi possível determinar um CRS métrico adequado."
            )

        return metric_crs

    @staticmethod
    def to_metric_crs(
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """
        Reprojeta a camada para um CRS métrico estimado.
        """

        usable_gdf = GeometryService.filter_usable_geometries(
            gdf
        )

        if usable_gdf.empty:
            return usable_gdf

        metric_crs = AreaService.estimate_metric_crs(
            usable_gdf
        )

        try:
            return usable_gdf.to_crs(
                metric_crs
            )

        except CRSError as error:
            raise ValueError(
                "Falha ao reprojetar a camada. "
                "Verifique o arquivo .prj do Shapefile."
            ) from error

    @staticmethod
    def total_area_hectares(
        gdf: gpd.GeoDataFrame,
    ) -> float:
        """
        Calcula a área total da camada em hectares.
        """

        metric_gdf = AreaService.to_metric_crs(
            gdf
        )

        if metric_gdf.empty:
            return 0.0

        return round(
            float(
                metric_gdf.geometry.area.sum()
                / 10000
            ),
            4,
        )

    @staticmethod
    def total_perimeter_meters(
        gdf: gpd.GeoDataFrame,
    ) -> float:
        """
        Calcula o perímetro ou comprimento total em metros.
        """

        metric_gdf = AreaService.to_metric_crs(
            gdf
        )

        if metric_gdf.empty:
            return 0.0

        return round(
            float(
                metric_gdf.geometry.length.sum()
            ),
            4,
        )

    @staticmethod
    def calculate_layer_statistics(
        gdf: gpd.GeoDataFrame,
    ) -> dict:
        """
        Retorna estatísticas métricas resumidas da camada.
        """

        if gdf is None or gdf.empty:
            return {
                "features": 0,
                "area_ha": 0.0,
                "perimeter_m": 0.0,
                "original_crs": None,
                "calculation_crs": None,
            }

        metric_crs = AreaService.estimate_metric_crs(
            gdf
        )

        metric_gdf = (
            GeometryService
            .filter_usable_geometries(gdf)
            .to_crs(metric_crs)
        )

        return {
            "features": len(gdf),
            "area_ha": round(
                float(
                    metric_gdf.geometry.area.sum()
                    / 10000
                ),
                4,
            ),
            "perimeter_m": round(
                float(
                    metric_gdf.geometry.length.sum()
                ),
                4,
            ),
            "original_crs": str(gdf.crs),
            "calculation_crs": metric_crs.to_string(),
        }

    @staticmethod
    def calculate_layers_statistics(
        layers: dict[str, gpd.GeoDataFrame],
    ) -> dict[str, dict]:
        """
        Calcula estatísticas para várias camadas.
        """

        results = {}

        for layer_name, gdf in layers.items():
            results[layer_name] = (
                AreaService.calculate_layer_statistics(
                    gdf
                )
            )

        return results