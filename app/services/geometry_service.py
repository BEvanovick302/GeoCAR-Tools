"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: geometry_service.py
Módulo......: Serviços de Geometria
Versão......: 4.0
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Centraliza operações geométricas reutilizáveis, como filtragem de
    geometrias válidas, contagem de multipartes, buracos internos e
    correção de geometrias inválidas.
===============================================================================
"""

from __future__ import annotations

import geopandas as gpd
from shapely.geometry import (
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Polygon,
)


class GeometryService:
    """
    Serviço de operações geométricas do GeoCAR Tools.
    """

    @staticmethod
    def usable_geometry_mask(
        gdf: gpd.GeoDataFrame,
    ):
        """
        Retorna uma máscara com geometrias não nulas e não vazias.
        """

        return (
            gdf.geometry.notna()
            & ~gdf.geometry.is_empty
        )

    @staticmethod
    def invalid_geometry_mask(
        gdf: gpd.GeoDataFrame,
    ):
        """
        Retorna uma máscara com geometrias utilizáveis e inválidas.
        """

        usable_mask = GeometryService.usable_geometry_mask(
            gdf
        )

        return (
            usable_mask
            & ~gdf.geometry.is_valid
        )

    @staticmethod
    def filter_usable_geometries(
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """
        Retorna apenas as feições com geometria utilizável.
        """

        mask = GeometryService.usable_geometry_mask(
            gdf
        )

        return gdf.loc[
            mask
        ].copy()

    @staticmethod
    def count_null_geometries(
        gdf: gpd.GeoDataFrame,
    ) -> int:
        """
        Conta geometrias nulas.
        """

        return int(
            gdf.geometry.isna().sum()
        )

    @staticmethod
    def count_empty_geometries(
        gdf: gpd.GeoDataFrame,
    ) -> int:
        """
        Conta geometrias vazias.
        """

        mask = (
            gdf.geometry.notna()
            & gdf.geometry.is_empty
        )

        return int(mask.sum())

    @staticmethod
    def count_invalid_geometries(
        gdf: gpd.GeoDataFrame,
    ) -> int:
        """
        Conta geometrias inválidas.
        """

        return int(
            GeometryService.invalid_geometry_mask(
                gdf
            ).sum()
        )

    @staticmethod
    def count_multipart_geometries(
        gdf: gpd.GeoDataFrame,
    ) -> int:
        """
        Conta geometrias multipartes.
        """

        multipart_types = (
            MultiPoint,
            MultiLineString,
            MultiPolygon,
        )

        return int(
            gdf.geometry.apply(
                lambda geometry: isinstance(
                    geometry,
                    multipart_types,
                )
            ).sum()
        )

    @staticmethod
    def count_duplicate_geometries(
        gdf: gpd.GeoDataFrame,
    ) -> int:
        """
        Conta geometrias duplicadas, desconsiderando nulas e vazias.
        """

        usable_gdf = (
            GeometryService.filter_usable_geometries(
                gdf
            )
        )

        if usable_gdf.empty:
            return 0

        return int(
            usable_gdf.geometry.duplicated().sum()
        )

    @staticmethod
    def count_interior_rings(
        gdf: gpd.GeoDataFrame,
    ) -> int:
        """
        Conta o total de anéis internos em polígonos e multipolígonos.
        """

        return int(
            gdf.geometry.apply(
                GeometryService._count_geometry_holes
            ).sum()
        )

    @staticmethod
    def fix_invalid_geometries(
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """
        Corrige geometrias inválidas usando make_valid().
        """

        corrected = gdf.copy()

        invalid_mask = (
            GeometryService.invalid_geometry_mask(
                corrected
            )
        )

        if not invalid_mask.any():
            return corrected

        corrected.loc[
            invalid_mask,
            "geometry",
        ] = (
            corrected.loc[
                invalid_mask,
                "geometry",
            ].make_valid()
        )

        return corrected

    @staticmethod
    def geometry_types(
        gdf: gpd.GeoDataFrame,
    ) -> list[str]:
        """
        Retorna os tipos geométricos presentes na camada.
        """

        return sorted(
            gdf.geometry.geom_type
            .dropna()
            .unique()
            .tolist()
        )

    @staticmethod
    def _count_geometry_holes(
        geometry,
    ) -> int:
        """
        Conta os anéis internos de uma geometria individual.
        """

        if geometry is None or geometry.is_empty:
            return 0

        if isinstance(geometry, Polygon):
            return len(
                geometry.interiors
            )

        if isinstance(geometry, MultiPolygon):
            return sum(
                len(polygon.interiors)
                for polygon in geometry.geoms
            )

        return 0