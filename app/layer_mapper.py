"""
===============================================================================
GeoCAR Tools
Versão 3.0
Mapeamento automático das camadas do SICAR
===============================================================================
"""


class LayerMapper:

    OFFICIAL_LAYERS = {

        "AREA_IMOVEL": [
            "AREA_IMOVEL",
            "AREA DO IMOVEL",
            "IMOVEL",
            "AREA_PROPERTY",
        ],

        "APP": [
            "APP",
            "AREA_PRESERVACAO_PERMANENTE",
            "AREA DE PRESERVACAO PERMANENTE",
        ],

        "RESERVA_LEGAL": [
            "RESERVA_LEGAL",
            "RL",
        ],

        "AREA_CONSOLIDADA": [
            "AREA_CONSOLIDADA",
            "AREA CONSOLIDADA",
            "AC",
        ],

        "VEGETACAO_NATIVA": [
            "VEGETACAO_NATIVA",
            "VEGETACAO NATIVA",
            "VN",
        ],

        "USO_RESTRITO": [
            "USO_RESTRITO",
        ],

        "HIDROGRAFIA": [
            "HIDROGRAFIA",
            "RIO",
            "LAGO",
            "NASCENTE",
        ],

        "SERVIDAO_ADMINISTRATIVA": [
            "SERVIDAO_ADMINISTRATIVA",
        ],

        "FLORESTA": [
            "FLORESTA",
        ],

    }

    @classmethod
    def normalize(cls, layer_name):

        if not layer_name:
            return "DESCONHECIDA"

        text = (
            str(layer_name)
            .upper()
            .replace("-", "_")
            .replace(" ", "_")
        )

        for official, aliases in cls.OFFICIAL_LAYERS.items():

            for alias in aliases:

                alias = (
                    alias.upper()
                    .replace("-", "_")
                    .replace(" ", "_")
                )

                if alias in text:
                    return official

        return "DESCONHECIDA"

    @classmethod
    def normalize_layers(cls, layers):

        normalized = {}

        for name, gdf in layers.items():

            official = cls.normalize(name)

            if official in normalized:

                normalized[official] = normalized[
                    official
                ]._append(
                    gdf,
                    ignore_index=True,
                )

            else:

                normalized[official] = gdf

        return normalized