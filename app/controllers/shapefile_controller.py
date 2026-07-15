"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: shapefile_controller.py
Módulo......: Controller do Shapefile
Versão......: 4.0
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Responsável por toda a lógica de manipulação de Shapefiles.
===============================================================================
"""

import geopandas as gpd

from app.importer import Importer
from app.services.geometry_service import GeometryService
from app.validators.geometry_validator import GeometryValidator


class ShapefileController:

    @staticmethod
    def load(path):
        """
        Carrega um shapefile e retorna todas as informações necessárias.
        """

        metadata = Importer.load_shapefile(path)

        gdf = gpd.read_file(path)

        validation = GeometryValidator.validate(
            gdf
        )

        return {

            "path": path,

            "gdf": gdf,

            "metadata": metadata,

            "validation": validation,

        }

    @staticmethod
    def fix(path):

        """
        Corrige um shapefile mantendo atributos.
        """

        gdf = gpd.read_file(path)

        corrected = (
            GeometryService.fix_invalid_geometries(
                gdf
            )
        )

        return corrected

    @staticmethod
    def statistics(gdf):

        """
        Estatísticas resumidas.
        """

        validation = (
            GeometryValidator.validate(
                gdf
            )
        )

        return {

            "features":
                validation["features"],

            "area_ha":
                validation["area_ha"],

            "perimeter_m":
                validation["perimeter_m"],

            "geometry_types":
                validation["geometry_types"],

            "invalid":
                validation["invalid_count"],

            "multipart":
                validation["multipart_count"],

            "duplicates":
                validation["duplicate_count"],

            "holes":
                validation["interior_rings_count"],

            "result":
                validation["result"],

        }

    @staticmethod
    def geometry_report(gdf):

        """
        Retorna um relatório completo da geometria.
        """

        return GeometryValidator.validate(
            gdf
        )

    @staticmethod
    def layer_summary(gdf):

        """
        Resumo simples para futuras telas.
        """

        report = (
            GeometryValidator.validate(
                gdf
            )
        )

        return {

            "features":
                report["features"],

            "area":
                report["area_ha"],

            "perimeter":
                report["perimeter_m"],

            "status":
                report["result"],

        }

    @staticmethod
    def compare(gdf_a, gdf_b):

        """
        Preparação para comparação de camadas (V4.1).
        """

        return {

            "features_a": len(gdf_a),

            "features_b": len(gdf_b),

            "area_a":
                GeometryValidator.validate(
                    gdf_a
                )["area_ha"],

            "area_b":
                GeometryValidator.validate(
                    gdf_b
                )["area_ha"],

            "difference":
                abs(

                    GeometryValidator.validate(
                        gdf_a
                    )["area_ha"]

                    -

                    GeometryValidator.validate(
                        gdf_b
                    )["area_ha"]

                )

        }