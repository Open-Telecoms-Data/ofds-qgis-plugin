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

    # Config for layers
    for table_name, table_info in schema_information["tables"].items():
        # Symbology https://github.com/Open-Telecoms-Data/ofds-qgis-plugin/issues/20
        if table_info["geographic_type"] == "LINESTRING":
            renderer = layers[table_name].renderer()
            symbol = renderer.symbol()
            symbol.setWidth(1.5)
            # spans_layer.triggerRepaint() may be needed, but as this point there is no data to repaint
        # Hide the GeoPackage ID field in all forms https://github.com/Open-Telecoms-Data/ofds-qgis-plugin/issues/29
        layers[table_name].setEditorWidgetSetup(0, QgsEditorWidgetSetup("Hidden", {}))
        # Fields
        for field_idx, field_info in enumerate(table_info["columns"]):
            if field_info["title"]:
                layers[table_name].setFieldAlias(field_idx + 1, field_info["title"])
            if field_info["type"] == "boolean":
                layers[table_name].setEditorWidgetSetup(
                    field_idx + 1,
                    QgsEditorWidgetSetup(
                        "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}
                    ),
                )
            elif field_info["type"] == "date":
                layers[table_name].setEditorWidgetSetup(
                    field_idx + 1,
                    QgsEditorWidgetSetup(
                        "DateTime",
                        {
                            "allow_null": True,
                            "calendar_popup": True,
                            "display_format": "yyyy-MM-dd",
                            "field_format": "yyyy-MM-dd",
                            "field_iso_format": False,
                        },
                    ),
                )
