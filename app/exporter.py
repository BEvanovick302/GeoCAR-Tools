"""
===============================================================================
GeoCAR Tools
Versão 3.0
Exportação padronizada das camadas do SICAR
===============================================================================
"""

import json
import os
import re
import unicodedata

import geopandas as gpd
import pandas as pd


class Exporter:

    GEOMETRY_FAMILIES = {
        "Point": "ponto",
        "MultiPoint": "ponto",
        "LineString": "linha",
        "MultiLineString": "linha",
        "Polygon": "poligono",
        "MultiPolygon": "poligono",
    }

    SHAPEFILE_COMPONENTS = (
        ".shp",
        ".shx",
        ".dbf",
        ".prj",
        ".cpg",
        ".qix",
    )

    @staticmethod
    def export_layers_as_shapefiles(
        layers,
        output_directory,
    ):

        if not layers:
            raise Exception(
                "Não existem camadas para exportar."
            )

        os.makedirs(
            output_directory,
            exist_ok=True,
        )

        exported = []
        manifest = []

        for layer_name, gdf in layers.items():

            if gdf is None or gdf.empty:
                continue

            geometry_layers = (
                Exporter._split_by_geometry_family(
                    gdf
                )
            )

            for family_name, family_gdf in (
                geometry_layers.items()
            ):

                if family_gdf.empty:
                    continue

                safe_layer_name = (
                    Exporter._sanitize_layer_name(
                        layer_name
                    )
                )

                file_name = (
                    f"{safe_layer_name}_"
                    f"{family_name}.shp"
                )

                output_path = os.path.join(
                    output_directory,
                    file_name,
                )

                prepared = (
                    Exporter._prepare_shapefile_data(
                        family_gdf
                    )
                )

                Exporter._remove_existing_shapefile(
                    output_path
                )

                prepared.to_file(
                    output_path,
                    driver="ESRI Shapefile",
                    encoding="utf-8",
                    index=False,
                )

                exported.append(
                    output_path
                )

                manifest.append(
                    {
                        "camada": layer_name,
                        "familia_geometrica": family_name,
                        "arquivo": file_name,
                        "quantidade": len(prepared),
                        "crs": str(prepared.crs),
                    }
                )

        if not exported:
            raise Exception(
                "Nenhuma camada válida foi exportada."
            )

        Exporter._write_manifest(
            output_directory,
            manifest,
        )

        return exported

    @staticmethod
    def export_geopackage(
        layers,
        output_path,
    ):

        if not layers:
            raise Exception(
                "Não existem camadas para exportar."
            )

        if not output_path.lower().endswith(".gpkg"):
            output_path += ".gpkg"

        output_directory = (
            os.path.dirname(output_path)
            or "."
        )

        os.makedirs(
            output_directory,
            exist_ok=True,
        )

        if os.path.exists(output_path):
            os.remove(output_path)

        exported_layers = 0

        for layer_name, gdf in layers.items():

            if gdf is None or gdf.empty:
                continue

            geometry_layers = (
                Exporter._split_by_geometry_family(
                    gdf
                )
            )

            for family_name, family_gdf in (
                geometry_layers.items()
            ):

                if family_gdf.empty:
                    continue

                safe_layer_name = (
                    Exporter._sanitize_layer_name(
                        layer_name
                    )
                )

                gpkg_layer_name = (
                    f"{safe_layer_name}_"
                    f"{family_name}"
                )

                prepared = (
                    Exporter._prepare_geopackage_data(
                        family_gdf
                    )
                )

                prepared.to_file(
                    output_path,
                    layer=gpkg_layer_name,
                    driver="GPKG",
                    index=False,
                )

                exported_layers += 1

        if exported_layers == 0:
            raise Exception(
                "Nenhuma camada válida foi exportada."
            )

        return output_path

    @staticmethod
    def _split_by_geometry_family(gdf):

        valid_gdf = gdf[
            gdf.geometry.notna()
            & ~gdf.geometry.is_empty
        ].copy()

        if valid_gdf.empty:
            return {}

        geometry_types = (
            valid_gdf.geometry.geom_type
        )

        result = {}

        for geometry_type, family_name in (
            Exporter.GEOMETRY_FAMILIES.items()
        ):

            mask = (
                geometry_types == geometry_type
            )

            if not mask.any():
                continue

            family_gdf = valid_gdf.loc[
                mask
            ].copy()

            if family_name not in result:

                result[family_name] = (
                    family_gdf
                )

            else:

                combined = pd.concat(
                    [
                        result[family_name],
                        family_gdf,
                    ],
                    ignore_index=True,
                )

                result[family_name] = (
                    gpd.GeoDataFrame(
                        combined,
                        geometry="geometry",
                        crs=gdf.crs,
                    )
                )

        return result

    @staticmethod
    def _prepare_shapefile_data(gdf):

        prepared = gdf.copy()

        geometry_column = (
            prepared.geometry.name
        )

        used_names = set()
        rename_columns = {}

        for column in prepared.columns:

            if column == geometry_column:
                continue

            rename_columns[column] = (
                Exporter._shapefile_field_name(
                    column,
                    used_names,
                )
            )

        prepared = prepared.rename(
            columns=rename_columns
        )

        for column in prepared.columns:

            if column == geometry_column:
                continue

            prepared[column] = (
                prepared[column].apply(
                    Exporter._normalize_attribute
                )
            )

        return gpd.GeoDataFrame(
            prepared,
            geometry=geometry_column,
            crs=gdf.crs,
        )

    @staticmethod
    def _prepare_geopackage_data(gdf):

        prepared = gdf.copy()

        geometry_column = (
            prepared.geometry.name
        )

        for column in prepared.columns:

            if column == geometry_column:
                continue

            prepared[column] = (
                prepared[column].apply(
                    Exporter._normalize_attribute
                )
            )

        return gpd.GeoDataFrame(
            prepared,
            geometry=geometry_column,
            crs=gdf.crs,
        )

    @staticmethod
    def _normalize_attribute(value):

        if value is None:
            return None

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(
            value,
            (
                dict,
                list,
                tuple,
                set,
            ),
        ):
            return json.dumps(
                value,
                ensure_ascii=False,
                default=str,
            )

        return str(value)

    @staticmethod
    def _shapefile_field_name(
        name,
        used_names,
    ):

        normalized = (
            Exporter._sanitize_layer_name(
                name
            )
        )

        normalized = (
            normalized[:10]
            or "campo"
        )

        candidate = normalized
        counter = 1

        while candidate in used_names:

            suffix = str(counter)

            candidate = (
                normalized[
                    : 10 - len(suffix)
                ]
                + suffix
            )

            counter += 1

        used_names.add(candidate)

        return candidate

    @staticmethod
    def _sanitize_layer_name(name):

        safe_name = unicodedata.normalize(
            "NFKD",
            str(name),
        )

        safe_name = safe_name.encode(
            "ascii",
            "ignore",
        ).decode("ascii")

        safe_name = safe_name.lower().strip()

        safe_name = re.sub(
            r"[^a-z0-9_]+",
            "_",
            safe_name,
        )

        safe_name = re.sub(
            r"_+",
            "_",
            safe_name,
        )

        return (
            safe_name.strip("_")
            or "camada"
        )

    @staticmethod
    def _remove_existing_shapefile(
        output_path,
    ):

        base_path = os.path.splitext(
            output_path
        )[0]

        for extension in (
            Exporter.SHAPEFILE_COMPONENTS
        ):

            component_path = (
                base_path + extension
            )

            if os.path.exists(
                component_path
            ):

                os.remove(
                    component_path
                )

    @staticmethod
    def _write_manifest(
        output_directory,
        manifest,
    ):

        manifest_path = os.path.join(
            output_directory,
            "camadas_sicar_exportadas.json",
        )

        with open(
            manifest_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                manifest,
                file,
                ensure_ascii=False,
                indent=4,
            )