"""
===============================================================================
GeoCAR Tools
MVP v1.9
===============================================================================
"""

import os

import geopandas as gpd
from PySide6.QtWidgets import QFileDialog
from shapely.geometry import MultiPolygon, Polygon


class Importer:

    REQUIRED_COMPONENTS = (".shp", ".shx", ".dbf", ".prj", ".cpg")

    @staticmethod
    def select_shapefile(parent):

        filename, _ = QFileDialog.getOpenFileName(
            parent,
            "Selecionar Shapefile",
            "",
            "Shapefile (*.shp)"
        )

        return filename

    @staticmethod
    def load_shapefile(path):

        components, missing = Importer._check_components(path)

        gdf = gpd.read_file(path)

        if gdf.empty:
            raise Exception("O shapefile não possui feições.")

        if gdf.crs is None:
            raise Exception("O shapefile não possui CRS.")

        calculation_crs = gdf.estimate_utm_crs()

        if calculation_crs is None:
            raise Exception(
                "Não foi possível determinar um CRS para cálculo."
            )

        calc = gdf.to_crs(calculation_crs)

        geometry_types = sorted(
            gdf.geom_type.dropna().unique().tolist()
        )

        invalid_count = int(
            (~gdf.geometry.is_valid).sum()
        )

        null_count = int(
            gdf.geometry.isna().sum()
        )

        empty_count = int(
            gdf.geometry.is_empty.sum()
        )

        multipart_count = int(
            gdf.geometry.apply(
                lambda g: isinstance(
                    g,
                    MultiPolygon
                )
            ).sum()
        )

        duplicate_count = int(
            gdf.geometry.astype(str).duplicated().sum()
        )

        interior_rings_count = int(
            gdf.geometry.apply(
                Importer.count_holes
            ).sum()
        )

        area = round(
            calc.area.sum() / 10000,
            2
        )

        perimeter = round(
            calc.length.sum(),
            2
        )

        overall = "Aprovado"

        if (
            invalid_count
            or null_count
            or empty_count
            or missing
        ):
            overall = "Requer atenção"

        return {

            "components": ", ".join(components),

            "missing_components":
                ", ".join(missing)
                if missing
                else "Nenhum",

            "crs": str(gdf.crs),

            "calculation_crs":
                calculation_crs.to_string(),

            "features": len(gdf),

            "geometry":
                gdf.geom_type.iloc[0],

            "geometry_types":
                ", ".join(geometry_types),

            "area_ha": area,

            "perimeter_m": perimeter,

            "is_valid":
                invalid_count == 0,

            "invalid_count":
                invalid_count,

            "null_count":
                null_count,

            "empty_count":
                empty_count,

            "multipart_count":
                multipart_count,

            "duplicate_count":
                duplicate_count,

            "interior_rings_count":
                interior_rings_count,

            "overall_result":
                overall,

        }

    @staticmethod
    def count_holes(geometry):

        if geometry is None:
            return 0

        if geometry.is_empty:
            return 0

        if isinstance(geometry, Polygon):
            return len(geometry.interiors)

        if isinstance(geometry, MultiPolygon):

            return sum(
                len(poly.interiors)
                for poly in geometry.geoms
            )

        return 0

    @staticmethod
    def _check_components(path):

        base = os.path.splitext(path)[0]

        found = []
        missing = []

        for ext in Importer.REQUIRED_COMPONENTS:

            file = base + ext

            if os.path.exists(file):
                found.append(ext)
            else:
                missing.append(ext)

        return found, missing

    @staticmethod
    def fix_invalid_geometries(parent, path):

        gdf = gpd.read_file(path)

        invalid = (
            gdf.geometry.notna()
            & (~gdf.geometry.is_valid)
        )

        if invalid.sum() == 0:
            raise Exception(
                "Não existem geometrias inválidas."
            )

        fixed = gdf.copy()

        fixed.loc[invalid, "geometry"] = (
            fixed.loc[
                invalid,
                "geometry"
            ].make_valid()
        )

        base = os.path.splitext(
            os.path.basename(path)
        )[0]

        output, _ = QFileDialog.getSaveFileName(
            parent,
            "Salvar Shapefile",
            f"{base}_corrigido.shp",
            "Shapefile (*.shp)"
        )

        if not output:
            return None

        if not output.lower().endswith(".shp"):
            output += ".shp"

        fixed.to_file(
            output,
            driver="ESRI Shapefile",
            encoding="utf-8"
        )

        return output