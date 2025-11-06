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
    for table_name, table_info in schema_information.items():
        layers[table_name] = QgsVectorLayer(
            filename + "|layername=" + table_name, table_name, "ogr"
        )
        layers[table_name].setCustomProperty("ofdslayer", table_name)
        group.insertChildNode(-1, QgsLayerTreeLayer(layers[table_name]))
        QgsProject.instance().addMapLayer(layers[table_name], False)

    # Symbology
    for table_name, table_info in schema_information.items():
        if table_info["geometry_type"] == "LINE":
            renderer = layers[table_name].renderer()
            symbol = renderer.symbol()
            symbol.setWidth(1.5)
            # spans_layer.triggerRepaint() may be needed, but as this point there is no data to repaint

    # Configure layer fields
    for table_name, table_info in schema_information.items():
        for field_idx, field_info in enumerate(table_info["fields"]):
            if field_info["type"] == "codelist":
                with open(
                    os.path.join(
                        PLUGIN_DIR,
                        "schema_0_3",
                        "codelists",
                        field_info["codelist_filename"],
                    )
                ) as csvfile:
                    csvreader = csv.reader(csvfile)
                    headers = next(csvreader)
                    values = []
                    for line in csvreader:
                        values.append({line[1]: line[0]})
                layers[table_name].setEditorWidgetSetup(
                    field_idx + 1, QgsEditorWidgetSetup("ValueMap", {"map": values})
                )
            elif field_info["type"] == "foreignkey":
                layers[table_name].setEditorWidgetSetup(
                    field_idx + 1,
                    QgsEditorWidgetSetup(
                        "ValueRelation",
                        {
                            "AllowMulti": False,
                            "AllowNull": True,
                            "Description": None,
                            "FilterExpression": None,
                            "Key": field_info["foreignkey_key"],
                            "Layer": layers[field_info["foreignkey_layer"]].id(),
                            "LayerName": field_info["foreignkey_layer"],
                            "LayerProviderName": "ogr",
                            "LayerSource": "{}|layername={}".format(
                                filename, field_info["foreignkey_layer"]
                            ),
                            "NofColumns": 1,
                            "OrderByValue": False,
                            "UseCompleter": False,
                            "Value": field_info["foreignkey_value"],
                        },
                    ),
                )
            elif field_info["type"] == "boolean":
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

            if field_info["alias"]:
                layers[table_name].setFieldAlias(field_idx + 1, field_info["alias"])
