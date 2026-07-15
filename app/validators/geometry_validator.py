"""
===============================================================================
GeoCAR Tools
-------------------------------------------------------------------------------
Arquivo.....: geometry_validator.py
Módulo......: Validador Geométrico
Versão......: 4.0
Autor.......: Brian Evanovick + OpenAI

Descrição...:
    Responsável pela validação geométrica das camadas utilizando os
    serviços centrais da aplicação.
===============================================================================
"""

from app.services.area_service import AreaService
from app.services.geometry_service import GeometryService


class GeometryValidator:

    @staticmethod
    def validate(gdf):

        stats = AreaService.calculate_layer_statistics(
            gdf
        )

        geometry_types = (
            GeometryService.geometry_types(
                gdf
            )
        )

        invalid = (
            GeometryService.count_invalid_geometries(
                gdf
            )
        )

        nulls = (
            GeometryService.count_null_geometries(
                gdf
            )
        )

        empty = (
            GeometryService.count_empty_geometries(
                gdf
            )
        )

        multipart = (
            GeometryService.count_multipart_geometries(
                gdf
            )
        )

        duplicate = (
            GeometryService.count_duplicate_geometries(
                gdf
            )
        )

        holes = (
            GeometryService.count_interior_rings(
                gdf
            )
        )

        approved = (

            invalid == 0
            and nulls == 0
            and empty == 0

        )

        return {

            "features":
                stats["features"],

            "area_ha":
                stats["area_ha"],

            "perimeter_m":
                stats["perimeter_m"],

            "original_crs":
                stats["original_crs"],

            "calculation_crs":
                stats["calculation_crs"],

            "geometry_types":
                ", ".join(geometry_types),

            "invalid_count":
                invalid,

            "null_count":
                nulls,

            "empty_count":
                empty,

            "multipart_count":
                multipart,

            "duplicate_count":
                duplicate,

            "interior_rings_count":
                holes,

            "approved":
                approved,

            "result":
                (
                    "Aprovado"
                    if approved
                    else "Requer atenção"
                )

        }

    @staticmethod
    def validate_layers(
        layers,
    ):

        results = {}

        for name, gdf in layers.items():

            results[name] = (
                GeometryValidator.validate(
                    gdf
                )
            )

        return results

    @staticmethod
    def summary(
        results,
    ):

        summary = {

            "layer_count": len(results),

            "feature_count": 0,

            "approved_layers": 0,

            "attention_layers": 0,

            "invalid_count": 0,

            "null_count": 0,

            "empty_count": 0,

            "duplicate_count": 0,

            "multipart_count": 0,

            "area_ha": 0,

        }

        for result in results.values():

            summary["feature_count"] += (
                result["features"]
            )

            summary["area_ha"] += (
                result["area_ha"]
            )

            summary["invalid_count"] += (
                result["invalid_count"]
            )

            summary["null_count"] += (
                result["null_count"]
            )

            summary["empty_count"] += (
                result["empty_count"]
            )

            summary["duplicate_count"] += (
                result["duplicate_count"]
            )

            summary["multipart_count"] += (
                result["multipart_count"]
            )

            if result["approved"]:

                summary["approved_layers"] += 1

            else:

                summary["attention_layers"] += 1

        summary["overall_result"] = (

            "Aprovado"

            if summary["attention_layers"] == 0

            else "Requer atenção"

        )

        summary["area_ha"] = round(
            summary["area_ha"],
            4,
        )

        return summary