import json
import os

from PyQt5.QtCore import QDate, Qt
from qgis.core import QgsProject, QgsVectorLayer

PLUGIN_DIR = os.path.dirname(__file__)


def find_layers():
    # Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)
    # Look
    layers = {}
    for k, v in QgsProject.instance().mapLayers().items():
        if isinstance(v, QgsVectorLayer):
            possible_layer = v.customProperty("ofdslayer")
            if possible_layer and possible_layer in schema_information["tables"].keys():
                layers[possible_layer] = v
    # If any of the layers are missing, return None.
    # That way downstream code can raise an alert on a simple "if" check
    # and can then trust all layers are present
    return None if [k for k, v in layers.items() if not v] else layers
