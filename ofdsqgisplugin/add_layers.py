import csv
import json
import os

from qgis.core import (QgsEditorWidgetSetup, QgsLayerTreeLayer, QgsProject,
                       QgsVectorLayer)

PLUGIN_DIR = os.path.dirname(__file__)


def add_layers(filename):
    # Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)

    # Create a group
    groupName = "Open Fibre"
    root = QgsProject.instance().layerTreeRoot()
    group = root.addGroup(groupName)

    # Add vector Layers
    layers = {}
    for table_name, table_info in schema_information["tables"].items():
        layers[table_name] = QgsVectorLayer(
            filename + "|layername=" + table_name, table_name, "ogr"
        )
        layers[table_name].setCustomProperty("ofdslayer", table_name)
        group.insertChildNode(-1, QgsLayerTreeLayer(layers[table_name]))
        QgsProject.instance().addMapLayer(layers[table_name], False)
