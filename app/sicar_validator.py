"""
===============================================================================
GeoCAR Tools
Versão 3.1
Validações específicas do SICAR
===============================================================================
"""

import geopandas as gpd


class SICARValidator:

    REQUIRED_LAYERS = {

        "AREA_IMOVEL",

        "APP",

        "RESERVA_LEGAL",

        "AREA_CONSOLIDADA",

        "VEGETACAO_NATIVA",

    }

    @staticmethod
    def validate(layers):

        report = {}

        report["existing_layers"] = sorted(
            layers.keys()
        )

        report["missing_layers"] = sorted(

            SICARValidator.REQUIRED_LAYERS
            - set(layers.keys())

        )

        report["layer_count"] = len(
            layers
        )

        report["required_ok"] = (
            len(report["missing_layers"]) == 0
        )

        report["areas"] = {}

        report["features"] = {}

        for name, gdf in layers.items():

            if gdf.empty:

                report["areas"][name] = 0

                report["features"][name] = 0

                continue

            calc = gdf.to_crs(
                gdf.estimate_utm_crs()
            )

            area = round(
                calc.area.sum() / 10000,
                2,
            )

            report["areas"][name] = area

            report["features"][name] = len(
                gdf
            )

        return report