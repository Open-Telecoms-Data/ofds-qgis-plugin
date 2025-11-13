import json
import os
import uuid

from qgis.core import QgsFeature, QgsJsonUtils

from .python.import_from_json import import_json_to_callable

PLUGIN_DIR = os.path.dirname(__file__)


def import_json(layers, json_data_to_import):
    # Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)
    # Setup
    for layer_id in layers:
        layers[layer_id].startEditing()

    # work
    def callable(table_name, data):
        feature = QgsFeature(layers[table_name].fields())
        for d in data:
            if d[0] != "geom":
                feature.setAttribute(d[0], d[1])
        if schema_information["tables"][table_name]["geographic_field"]:
            geom_data = [d[1] for d in data if d[0] == "geom"]
            if geom_data and geom_data[0]:
                feature.setGeometry(QgsJsonUtils.geometryFromGeoJson(geom_data[0]))
        if not layers[table_name].addFeature(feature):
            raise Exception("Could not add to table_name layer")

    import_json_to_callable(json_data_to_import, callable)
    # Commit
    for layer_id in layers:
        if not layers[layer_id].commitChanges():
            raise Exception("Could not commit {} layer".format(layer_id))
