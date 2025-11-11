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
            if possible_layer and possible_layer in schema_information.keys():
                layers[possible_layer] = v
    # If any of the layers are missing, return None.
    # That way downstream code can raise an alert on a simple "if" check
    # and can then trust all layers are present
    return None if [k for k, v in layers.items() if not v] else layers


def set_key_in_dict_for_export(data, key, value, type=""):
    if not value:
        return
    key_bits = key.split("/")
    final_key = key_bits.pop(-1)
    for key_bit in key_bits:
        if key_bit in data:
            data = data[key_bit]
        else:
            data[key_bit] = {}
            data = data[key_bit]
    if isinstance(value, QDate):
        data[final_key] = value.toString(Qt.ISODate)
    elif type == "boolean":
        data[final_key] = value == "true"
    elif type == "integer":
        data[final_key] = int(value)
    elif type == "number":
        data[final_key] = float(value)
    else:
        data[final_key] = value


def get_deep_key_from_data_for_import(data, key):
    key_bits = key.split("/")
    final_key = key_bits.pop(-1)
    for key_bit in key_bits:
        if key_bit in data and isinstance(data[key_bit], dict):
            data = data[key_bit]
        else:
            return None
    return data.get(final_key)
