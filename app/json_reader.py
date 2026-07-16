"""
===============================================================================
GeoCAR Tools
Versão 3.0
Leitura e padronização das camadas do JSON
===============================================================================
"""

import json
import re
import unicodedata

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

from app.layer_mapper import LayerMapper


class JsonReader:

    DEFAULT_CRS = "EPSG:4674"

    GEOMETRY_TYPES = (
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
        "Polygon",
        "MultiPolygon",
        "GeometryCollection",
    )

    LAYER_FIELDS = (
        "layer",
        "camada",
        "categoria",
        "nome",
        "name",
        "tipo",
        "classe",
        "descricao",
        "description",
    )

    @staticmethod
    def open(path):

        encodings = (
            "utf-8-sig",
            "utf-8",
            "latin-1",
        )

        last_error = None

        for encoding in encodings:

            try:

                with open(
                    path,
                    "r",
                    encoding=encoding,
                ) as file:

                    return json.load(file)

            except UnicodeDecodeError as error:
                last_error = error

        raise Exception(
            f"Não foi possível ler o JSON: {last_error}"
        )

    @staticmethod
    def summary(data):

        layers = JsonReader.extract_layers(data)

        geometry_types = {}

        for gdf in layers.values():

            counts = (
                gdf.geometry.geom_type
                .value_counts()
            )

            for geometry_type, count in counts.items():

                geometry_types[geometry_type] = (
                    geometry_types.get(
                        geometry_type,
                        0,
                    )
                    + int(count)
                )

        recibo = "-"
        protocolo = "-"

        if isinstance(data, dict):

            def procurar(obj, campo):

                if isinstance(obj, dict):

                    if campo in obj:
                        return obj[campo]

                    for valor in obj.values():

                        resultado = procurar(
                            valor,
                            campo,
                        )

                        if resultado is not None:
                            return resultado

                elif isinstance(obj, list):

                    for item in obj:

                        resultado = procurar(
                            item,
                            campo,
                        )

                        if resultado is not None:
                            return resultado

                return None

            valor = procurar(
                data,
                "idPai",
            )

            if valor is not None:
                recibo = str(valor)

            valor = procurar(
                data,
                "codigoProtocolo",
            )

            if valor is not None:
                protocolo = str(valor)

        return {
            "type": type(data).__name__,

            "items": JsonReader.count_items(data),

            "layers": sorted(
                layers.keys()
            ),

            "layer_count": len(layers),

            "geometry_count": sum(
                len(gdf)
                for gdf in layers.values()
            ),

            "geometry_types": geometry_types,

            "polygon_count": geometry_types.get(
                "Polygon",
                0,
            ),

            "multipolygon_count": geometry_types.get(
                "MultiPolygon",
                0,
            ),

            "point_count": (
                geometry_types.get(
                    "Point",
                    0,
                )
                + geometry_types.get(
                    "MultiPoint",
                    0,
                )
            ),

            "line_count": (
                geometry_types.get(
                    "LineString",
                    0,
                )
                + geometry_types.get(
                    "MultiLineString",
                    0,
                )
            ),

            "idPai": recibo,

            "codigoProtocolo": protocolo,
        }

    @staticmethod
    def extract_layers(data):

        detected_crs = JsonReader.detect_crs(data)

        layer_records = {}

        JsonReader._walk_json(
            obj=data,
            layer_records=layer_records,
            current_layer="DESCONHECIDA",
            inherited_properties={},
        )

        raw_layers = {}

        for layer_name, records in layer_records.items():

            if not records:
                continue

            gdf = gpd.GeoDataFrame(
                records,
                geometry="geometry",
                crs=detected_crs,
            )

            valid_mask = (
                gdf.geometry.notna()
                & ~gdf.geometry.is_empty
            )

            gdf = gdf.loc[
                valid_mask
            ].reset_index(drop=True)

            if not gdf.empty:
                raw_layers[layer_name] = gdf

        return JsonReader._normalize_layers(
            raw_layers
        )

    @staticmethod
    def _normalize_layers(layers):

        normalized_layers = {}

        for layer_name, gdf in layers.items():

            official_name = LayerMapper.normalize(
                layer_name
            )

            if official_name not in normalized_layers:

                normalized_layers[official_name] = (
                    gdf.copy()
                )

                continue

            combined = pd.concat(
                [
                    normalized_layers[official_name],
                    gdf,
                ],
                ignore_index=True,
            )

            normalized_layers[official_name] = (
                gpd.GeoDataFrame(
                    combined,
                    geometry="geometry",
                    crs=gdf.crs,
                )
            )

        return normalized_layers

    @staticmethod
    def detect_crs(data):

        if not isinstance(data, dict):
            return JsonReader.DEFAULT_CRS

        crs_data = data.get("crs")

        if isinstance(crs_data, str):

            match = re.search(
                r"EPSG[:/]{0,2}(\d+)",
                crs_data,
                re.IGNORECASE,
            )

            if match:
                return f"EPSG:{match.group(1)}"

        if not isinstance(crs_data, dict):
            return JsonReader.DEFAULT_CRS

        properties = crs_data.get(
            "properties",
            {},
        )

        crs_name = properties.get("name")

        if not isinstance(crs_name, str):
            return JsonReader.DEFAULT_CRS

        match = re.search(
            r"EPSG(?::|::|/0/)(\d+)",
            crs_name,
            re.IGNORECASE,
        )

        if match:
            return f"EPSG:{match.group(1)}"

        return JsonReader.DEFAULT_CRS

    @staticmethod
    def _walk_json(
        obj,
        layer_records,
        current_layer,
        inherited_properties,
    ):

        if isinstance(obj, list):

            for item in obj:

                JsonReader._walk_json(
                    obj=item,
                    layer_records=layer_records,
                    current_layer=current_layer,
                    inherited_properties=(
                        inherited_properties
                    ),
                )

            return

        if not isinstance(obj, dict):
            return

        detected_layer = JsonReader._detect_layer(
            obj,
            current_layer,
        )

        object_type = obj.get("type")

        if object_type == "FeatureCollection":

            for feature in obj.get(
                "features",
                [],
            ):

                JsonReader._walk_json(
                    obj=feature,
                    layer_records=layer_records,
                    current_layer=detected_layer,
                    inherited_properties=(
                        inherited_properties
                    ),
                )

            return

        if object_type == "Feature":

            properties = dict(
                inherited_properties
            )

            feature_properties = obj.get(
                "properties",
                {},
            )

            if isinstance(
                feature_properties,
                dict,
            ):

                properties.update(
                    JsonReader._simple_properties(
                        feature_properties
                    )
                )

            feature_layer = (
                JsonReader._detect_layer(
                    feature_properties,
                    detected_layer,
                )
            )

            JsonReader._add_geometry(
                geometry_data=obj.get("geometry"),
                layer_name=feature_layer,
                properties=properties,
                layer_records=layer_records,
            )

            return

        if object_type in JsonReader.GEOMETRY_TYPES:

            JsonReader._add_geometry(
                geometry_data=obj,
                layer_name=detected_layer,
                properties=inherited_properties,
                layer_records=layer_records,
            )

            return

        properties = dict(
            inherited_properties
        )

        properties.update(
            JsonReader._simple_properties(obj)
        )

        for key, value in obj.items():

            if not isinstance(
                value,
                (dict, list),
            ):
                continue

            next_layer = detected_layer

            if JsonReader._looks_like_layer(key):

                next_layer = (
                    JsonReader._normalize_layer_name(
                        key
                    )
                )

            JsonReader._walk_json(
                obj=value,
                layer_records=layer_records,
                current_layer=next_layer,
                inherited_properties=properties,
            )

    @staticmethod
    def _add_geometry(
        geometry_data,
        layer_name,
        properties,
        layer_records,
    ):

        if not isinstance(
            geometry_data,
            dict,
        ):
            return

        geometry_type = geometry_data.get(
            "type"
        )

        if geometry_type == "GeometryCollection":

            for geometry_item in geometry_data.get(
                "geometries",
                [],
            ):

                JsonReader._add_geometry(
                    geometry_data=geometry_item,
                    layer_name=layer_name,
                    properties=properties,
                    layer_records=layer_records,
                )

            return

        if geometry_type not in JsonReader.GEOMETRY_TYPES:
            return

        try:
            geometry = shape(geometry_data)

        except Exception:
            return

        if geometry is None or geometry.is_empty:
            return

        safe_layer_name = (
            JsonReader._normalize_layer_name(
                layer_name
            )
        )

        record = dict(properties)
        record["geometry"] = geometry

        layer_records.setdefault(
            safe_layer_name,
            [],
        ).append(record)

    @staticmethod
    def _detect_layer(
        obj,
        fallback,
    ):

        if not isinstance(obj, dict):
            return fallback

        for field in JsonReader.LAYER_FIELDS:

            value = obj.get(field)

            if (
                isinstance(value, str)
                and value.strip()
            ):

                return (
                    JsonReader._normalize_layer_name(
                        value
                    )
                )

        return fallback

    @staticmethod
    def _looks_like_layer(value):

        normalized = (
            JsonReader._normalize_layer_name(
                value
            )
        )

        return (
            LayerMapper.normalize(normalized)
            != "DESCONHECIDA"
        )

    @staticmethod
    def _simple_properties(obj):

        if not isinstance(obj, dict):
            return {}

        properties = {}

        for key, value in obj.items():

            if isinstance(
                value,
                (
                    str,
                    int,
                    float,
                    bool,
                ),
            ) or value is None:

                safe_key = (
                    JsonReader._normalize_field_name(
                        key
                    )
                )

                properties[safe_key] = value

        return properties

    @staticmethod
    def _normalize_layer_name(value):

        normalized = unicodedata.normalize(
            "NFKD",
            str(value),
        )

        normalized = normalized.encode(
            "ascii",
            "ignore",
        ).decode("ascii")

        normalized = normalized.upper().strip()

        normalized = re.sub(
            r"[^A-Z0-9_]+",
            "_",
            normalized,
        )

        normalized = re.sub(
            r"_+",
            "_",
            normalized,
        )

        return (
            normalized.strip("_")
            or "DESCONHECIDA"
        )

    @staticmethod
    def _normalize_field_name(value):

        normalized = unicodedata.normalize(
            "NFKD",
            str(value),
        )

        normalized = normalized.encode(
            "ascii",
            "ignore",
        ).decode("ascii")

        normalized = normalized.lower().strip()

        normalized = re.sub(
            r"[^a-z0-9_]+",
            "_",
            normalized,
        )

        normalized = re.sub(
            r"_+",
            "_",
            normalized,
        )

        return (
            normalized.strip("_")
            or "atributo"
        )

    @staticmethod
    def count_items(data):

        if isinstance(data, (dict, list)):
            return len(data)

        return 0