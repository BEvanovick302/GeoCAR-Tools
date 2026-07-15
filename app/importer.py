"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: importer.py
Módulo......: Importação de Shapefile
Versão......: 4.0.1
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Realiza a leitura inicial do Shapefile sem executar reprojeções.
===============================================================================
"""

import os

import geopandas as gpd
from PySide6.QtWidgets import QFileDialog

from app.services.geometry_service import GeometryService


class Importer:

    REQUIRED_COMPONENTS = (
        ".shp",
        ".shx",
        ".dbf",
        ".prj",
        ".cpg",
    )

    @staticmethod
    def select_shapefile(parent):

        filename, _ = QFileDialog.getOpenFileName(
            parent,
            "Selecionar Shapefile",
            "",
            "Shapefile (*.shp)",
        )

        return filename

    @staticmethod
    def load_shapefile(path):

        components, missing = (
            Importer._check_components(path)
        )

        gdf = gpd.read_file(path)

        if gdf.empty:
            raise ValueError(
                "O Shapefile não possui feições."
            )

        crs_text = (
            str(gdf.crs)
            if gdf.crs is not None
            else "Não definido"
        )

        geometry_types = (
            GeometryService.geometry_types(gdf)
        )

        invalid_count = (
            GeometryService.count_invalid_geometries(
                gdf
            )
        )

        null_count = (
            GeometryService.count_null_geometries(
                gdf
            )
        )

        empty_count = (
            GeometryService.count_empty_geometries(
                gdf
            )
        )

        multipart_count = (
            GeometryService.count_multipart_geometries(
                gdf
            )
        )

        duplicate_count = (
            GeometryService.count_duplicate_geometries(
                gdf
            )
        )

        interior_rings_count = (
            GeometryService.count_interior_rings(
                gdf
            )
        )

        overall = "Aprovado"

        if (
            invalid_count > 0
            or null_count > 0
            or empty_count > 0
            or missing
            or gdf.crs is None
        ):
            overall = "Requer atenção"

        return {
            "components": ", ".join(components),
            "missing_components": (
                ", ".join(missing)
                if missing
                else "Nenhum"
            ),
            "crs": crs_text,
            "features": len(gdf),
            "geometry": (
                geometry_types[0]
                if geometry_types
                else "Desconhecida"
            ),
            "geometry_types": ", ".join(
                geometry_types
            ),
            "is_valid": (
                invalid_count == 0
                and null_count == 0
                and empty_count == 0
            ),
            "invalid_count": invalid_count,
            "null_count": null_count,
            "empty_count": empty_count,
            "multipart_count": multipart_count,
            "duplicate_count": duplicate_count,
            "interior_rings_count": (
                interior_rings_count
            ),
            "overall_result": overall,
        }

    @staticmethod
    def _check_components(path):

        base_path = os.path.splitext(path)[0]

        found = []
        missing = []

        for extension in (
            Importer.REQUIRED_COMPONENTS
        ):
            component_path = (
                base_path + extension
            )

            if os.path.exists(component_path):
                found.append(extension)
            else:
                missing.append(extension)

        return found, missing

    @staticmethod
    def fix_invalid_geometries(
        parent,
        path,
    ):

        gdf = gpd.read_file(path)

        corrected = (
            GeometryService.fix_invalid_geometries(
                gdf
            )
        )

        if corrected.geometry.equals(
            gdf.geometry
        ):
            raise ValueError(
                "Não existem geometrias inválidas."
            )

        base_name = os.path.splitext(
            os.path.basename(path)
        )[0]

        output_path, _ = (
            QFileDialog.getSaveFileName(
                parent,
                "Salvar Shapefile corrigido",
                f"{base_name}_corrigido.shp",
                "Shapefile (*.shp)",
            )
        )

        if not output_path:
            return None

        if not output_path.lower().endswith(
            ".shp"
        ):
            output_path += ".shp"

        corrected.to_file(
            output_path,
            driver="ESRI Shapefile",
            encoding="utf-8",
            index=False,
        )

        return output_path