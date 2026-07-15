"""
===============================================================================
GeoCAR Tools
Versão 2.5
Validação das camadas extraídas do JSON
===============================================================================
"""

from shapely.geometry import (
    MultiLineString,
    MultiPoint,
    MultiPolygon,
)


class JsonValidator:

    @staticmethod
    def validate_layers(layers):

        if not layers:
            raise Exception(
                "Nenhuma camada JSON foi encontrada."
            )

        results = {}

        for layer_name, gdf in layers.items():

            results[layer_name] = (
                JsonValidator.validate_layer(gdf)
            )

        return results

    @staticmethod
    def validate_layer(gdf):

        if gdf is None or gdf.empty:

            return {
                "features": 0,
                "geometry_types": "",
                "null_count": 0,
                "empty_count": 0,
                "invalid_count": 0,
                "multipart_count": 0,
                "duplicate_count": 0,
                "is_valid": False,
                "result": "Camada vazia",
            }

        null_mask = gdf.geometry.isna()

        empty_mask = (
            gdf.geometry.notna()
            & gdf.geometry.is_empty
        )

        usable_mask = (
            gdf.geometry.notna()
            & ~gdf.geometry.is_empty
        )

        invalid_mask = (
            usable_mask
            & ~gdf.geometry.is_valid
        )

        multipart_count = int(
            gdf.geometry.apply(
                JsonValidator._is_multipart
            ).sum()
        )

        duplicate_count = int(
            gdf.loc[
                usable_mask,
                "geometry",
            ].duplicated().sum()
        )

        geometry_types = sorted(
            gdf.geometry.geom_type
            .dropna()
            .unique()
            .tolist()
        )

        null_count = int(
            null_mask.sum()
        )

        empty_count = int(
            empty_mask.sum()
        )

        invalid_count = int(
            invalid_mask.sum()
        )

        is_valid = (
            null_count == 0
            and empty_count == 0
            and invalid_count == 0
        )

        result = (
            "Aprovado"
            if is_valid
            else "Requer atenção"
        )

        return {
            "features": len(gdf),
            "geometry_types": ", ".join(
                geometry_types
            ),
            "null_count": null_count,
            "empty_count": empty_count,
            "invalid_count": invalid_count,
            "multipart_count": multipart_count,
            "duplicate_count": duplicate_count,
            "is_valid": is_valid,
            "result": result,
        }

    @staticmethod
    def create_summary(results):

        layer_count = len(results)

        feature_count = sum(
            result["features"]
            for result in results.values()
        )

        invalid_count = sum(
            result["invalid_count"]
            for result in results.values()
        )

        null_count = sum(
            result["null_count"]
            for result in results.values()
        )

        empty_count = sum(
            result["empty_count"]
            for result in results.values()
        )

        duplicate_count = sum(
            result["duplicate_count"]
            for result in results.values()
        )

        approved_layers = sum(
            result["is_valid"]
            for result in results.values()
        )

        return {
            "layer_count": layer_count,
            "feature_count": feature_count,
            "invalid_count": invalid_count,
            "null_count": null_count,
            "empty_count": empty_count,
            "duplicate_count": duplicate_count,
            "approved_layers": approved_layers,
            "attention_layers": (
                layer_count - approved_layers
            ),
            "overall_result": (
                "Aprovado"
                if approved_layers == layer_count
                else "Requer atenção"
            ),
        }

    @staticmethod
    def _is_multipart(geometry):

        return isinstance(
            geometry,
            (
                MultiPoint,
                MultiLineString,
                MultiPolygon,
            ),
        )