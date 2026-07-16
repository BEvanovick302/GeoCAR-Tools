"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: comparison_service.py
Módulo......: Serviço de Comparação Espacial
Versão......: 4.1
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Compara uma camada extraída do JSON com um Shapefile, calculando
    áreas, diferenças, interseção e percentuais de correspondência.
===============================================================================
"""

from __future__ import annotations

from typing import Any

import geopandas as gpd
from shapely.ops import unary_union

from app.services.area_service import AreaService
from app.services.geometry_service import GeometryService


class ComparisonService:
    """
    Serviço responsável pela comparação entre camadas geográficas.
    """

    @staticmethod
    def compare(
        json_gdf: gpd.GeoDataFrame,
        shapefile_gdf: gpd.GeoDataFrame,
    ) -> dict[str, Any]:
        """
        Compara uma camada JSON com um Shapefile.
        """

        if json_gdf is None or json_gdf.empty:
            raise ValueError(
                "A camada JSON está vazia."
            )

        if shapefile_gdf is None or shapefile_gdf.empty:
            raise ValueError(
                "O Shapefile está vazio."
            )

        json_usable = (
            GeometryService.filter_usable_geometries(
                json_gdf
            )
        )

        shape_usable = (
            GeometryService.filter_usable_geometries(
                shapefile_gdf
            )
        )

        if json_usable.empty:
            raise ValueError(
                "A camada JSON não possui geometrias utilizáveis."
            )

        if shape_usable.empty:
            raise ValueError(
                "O Shapefile não possui geometrias utilizáveis."
            )

        target_crs = (
            ComparisonService._resolve_target_crs(
                json_usable,
                shape_usable,
            )
        )

        json_metric = json_usable.to_crs(
            target_crs
        )

        shape_metric = shape_usable.to_crs(
            target_crs
        )

        json_geometry = unary_union(
            json_metric.geometry
        )

        shape_geometry = unary_union(
            shape_metric.geometry
        )

        json_area_ha = round(
            float(json_geometry.area / 10000),
            4,
        )

        shapefile_area_ha = round(
            float(shape_geometry.area / 10000),
            4,
        )

        intersection_geometry = (
            json_geometry.intersection(
                shape_geometry
            )
        )

        json_difference_geometry = (
            json_geometry.difference(
                shape_geometry
            )
        )

        shapefile_difference_geometry = (
            shape_geometry.difference(
                json_geometry
            )
        )

        intersection_area_ha = round(
            float(
                intersection_geometry.area
                / 10000
            ),
            4,
        )

        json_difference_area_ha = round(
            float(
                json_difference_geometry.area
                / 10000
            ),
            4,
        )

        shapefile_difference_area_ha = round(
            float(
                shapefile_difference_geometry.area
                / 10000
            ),
            4,
        )

        absolute_area_difference_ha = round(
            abs(
                json_area_ha
                - shapefile_area_ha
            ),
            4,
        )

        reference_area = max(
            json_area_ha,
            shapefile_area_ha,
        )

        area_difference_percent = (
            round(
                (
                    absolute_area_difference_ha
                    / reference_area
                    * 100
                ),
                4,
            )
            if reference_area > 0
            else 0.0
        )

        intersection_percent_json = (
            round(
                (
                    intersection_area_ha
                    / json_area_ha
                    * 100
                ),
                4,
            )
            if json_area_ha > 0
            else 0.0
        )

        intersection_percent_shapefile = (
            round(
                (
                    intersection_area_ha
                    / shapefile_area_ha
                    * 100
                ),
                4,
            )
            if shapefile_area_ha > 0
            else 0.0
        )

        status = (
            "Compatível"
            if area_difference_percent <= 0.01
            else "Requer análise"
        )

        return {
            "json_features": len(json_gdf),
            "shapefile_features": len(
                shapefile_gdf
            ),
            "json_area_ha": json_area_ha,
            "shapefile_area_ha": (
                shapefile_area_ha
            ),
            "absolute_area_difference_ha": (
                absolute_area_difference_ha
            ),
            "area_difference_percent": (
                area_difference_percent
            ),
            "intersection_area_ha": (
                intersection_area_ha
            ),
            "intersection_percent_json": (
                intersection_percent_json
            ),
            "intersection_percent_shapefile": (
                intersection_percent_shapefile
            ),
            "json_difference_area_ha": (
                json_difference_area_ha
            ),
            "shapefile_difference_area_ha": (
                shapefile_difference_area_ha
            ),
            "calculation_crs": (
                target_crs.to_string()
            ),
            "status": status,
        }

    @staticmethod
    def _resolve_target_crs(
        json_gdf: gpd.GeoDataFrame,
        shapefile_gdf: gpd.GeoDataFrame,
    ):
        """
        Define um CRS métrico comum para a comparação.
        """

        if json_gdf.crs is None:
            raise ValueError(
                "A camada JSON não possui CRS definido."
            )

        if shapefile_gdf.crs is None:
            raise ValueError(
                "O Shapefile não possui CRS definido."
            )

        try:
            return AreaService.estimate_metric_crs(
                json_gdf
            )

        except Exception:
            return AreaService.estimate_metric_crs(
                shapefile_gdf
            )