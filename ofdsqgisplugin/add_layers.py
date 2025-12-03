import csv
import json
import os

from qgis.core import (Qgis, QgsAttributeEditorRelation, QgsDefaultValue,
                       QgsEditFormConfig, QgsEditorWidgetSetup,
                       QgsLayerTreeLayer, QgsMapLayer, QgsProject, QgsRelation,
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
            elif (
                field_info["type"] == "open_codelist"
                or field_info["type"] == "closed_codelist"
            ):
                values = schema_information[
                    (
                        "open_codelists"
                        if field_info["type"] == "open_codelist"
                        else "closed_codelists"
                    )
                ][field_info["codelist"]]
                values = [{i[1]: i[0]} for i in values]
                layers[table_name].setEditorWidgetSetup(
                    field_idx + 1,
                    QgsEditorWidgetSetup("ValueMap", {"map": values}),
                )
            elif (
                field_info["type"] == "foreign_key_id_name_dict"
                or field_info["type"] == "foreign_key"
            ):
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
            if field_info["type"] == "text" and field_info["name"] == "ofds_id":
                layers[table_name].setDefaultValueDefinition(
                    field_idx + 1,
                    QgsDefaultValue(
                        "ltrim(rtrim(uuid(),'}'),'{')"
                        if table_name == "networks"
                        else "count('{}') + 1".format(table_name)
                    ),
                )

        # Relations
        for relation in table_info["relations"]:

            # Load join table
            layers[relation["mapping_table"]] = QgsVectorLayer(
                filename + "|layername=" + relation["mapping_table"],
                relation["mapping_table"],
                "ogr",
            )
            layers[relation["mapping_table"]].setCustomProperty(
                "ofdslayer", relation["mapping_table"]
            )
            layers[relation["mapping_table"]].setFlags(QgsMapLayer.Private)
            group.insertChildNode(
                -1, QgsLayerTreeLayer(layers[relation["mapping_table"]])
            )
            QgsProject.instance().addMapLayer(layers[relation["mapping_table"]], False)

            # Create relationships
            join_to_base = QgsRelation()
            join_to_base.setName("join_to_base_" + relation["name"])
            join_to_base.setId("join_to_base_" + relation["name"])
            join_to_base.setReferencingLayer(layers[relation["mapping_table"]].id())
            join_to_base.setReferencedLayer(layers[table_name].id())
            join_to_base.addFieldPair("base_id", "id")
            QgsProject.instance().relationManager().addRelation(join_to_base)

            join_to_related = QgsRelation()
            join_to_related.setName("join_to_related_" + relation["name"])
            join_to_related.setId("join_to_related_" + relation["name"])
            join_to_related.setReferencingLayer(layers[relation["mapping_table"]].id())
            join_to_related.setReferencedLayer(layers[relation["related_table"]].id())
            join_to_related.addFieldPair("related_id", "id")
            QgsProject.instance().relationManager().addRelation(join_to_related)

            # Set up form widget
            form_config = layers[table_name].editFormConfig()
            relation_editor = QgsAttributeEditorRelation(join_to_base, None)
            relation_editor.setLabel(relation["title"])
            # set's cardinality option
            relation_editor.setNmRelationId(join_to_related.id())
            # set's mode to "Drag and drop designer"
            form_config.setLayout(QgsEditFormConfig.TabLayout)
            form_config.invisibleRootContainer().addChildElement(relation_editor)
            layers[table_name].setEditFormConfig(form_config)

    # Project Properties
    QgsProject.instance().setTransactionMode(Qgis.TransactionMode.AutomaticGroups)
