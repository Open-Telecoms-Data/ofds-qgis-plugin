import csv
import json
import os

from qgis.core import (Qgis, QgsAttributeEditorContainer,
                       QgsAttributeEditorRelation, QgsDefaultValue,
                       QgsEditFormConfig, QgsEditorWidgetSetup,
                       QgsLayerTreeLayer, QgsMapLayer, QgsProject, QgsRelation,
                       QgsVectorLayer)

PLUGIN_DIR = os.path.dirname(__file__)


def add_layers(filename, plugin, custom_ui=False):
    # --------   Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)

    # --------   Create a group
    groupName = "Open Fibre"
    root = QgsProject.instance().layerTreeRoot()
    group = root.addGroup(groupName)

    # --------  Add vector Layers
    layers = {}
    for table_name, table_info in schema_information["tables"].items():
        layers[table_name] = QgsVectorLayer(
            filename + "|layername=" + table_name, table_name, "ogr"
        )
        layers[table_name].setCustomProperty("ofdslayer", table_name)
        group.insertChildNode(-1, QgsLayerTreeLayer(layers[table_name]))
        QgsProject.instance().addMapLayer(layers[table_name], False)

    # --------   Config for layers
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

            # --------  boolean
            if field_info["type"] == "boolean":
                layers[table_name].setEditorWidgetSetup(
                    field_idx + 1,
                    QgsEditorWidgetSetup(
                        "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}
                    ),
                )

            # --------  date
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

            # --------  closed codelist
            elif field_info["type"] == "closed_codelist":
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

            # --------  open codelist
            elif field_info["type"] == "open_codelist":
                codelist_layer_name = "codelist_open_" + field_info["codelist"][:-4]
                # If we need to, load the target table
                if codelist_layer_name not in layers:
                    layers[codelist_layer_name] = QgsVectorLayer(
                        filename + "|layername=" + codelist_layer_name,
                        codelist_layer_name,
                        "ogr",
                    )
                    layers[codelist_layer_name].setCustomProperty(
                        "ofdslayer", codelist_layer_name
                    )
                    group.insertChildNode(
                        -1, QgsLayerTreeLayer(layers[codelist_layer_name])
                    )
                    QgsProject.instance().addMapLayer(
                        layers[codelist_layer_name], False
                    )
                # config widget
                layers[table_name].setEditorWidgetSetup(
                    field_idx + 1,
                    QgsEditorWidgetSetup(
                        "ValueRelation",
                        {
                            "AllowMulti": False,
                            "AllowNull": True,
                            "Description": None,
                            "FilterExpression": None,
                            "Key": "id",
                            "Layer": layers[codelist_layer_name].id(),
                            "LayerName": codelist_layer_name,
                            "LayerProviderName": "ogr",
                            "LayerSource": "{}|layername={}".format(
                                filename, codelist_layer_name
                            ),
                            "NofColumns": 1,
                            "OrderByValue": False,
                            "UseCompleter": False,
                            "Value": "description",
                        },
                    ),
                )

            # --------  foreign key (both types, direct and dict with id and name)
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

            # --------  for ocds id fields, set default value
            if field_info["type"] == "text" and field_info["name"] == "ofds_id":
                layers[table_name].setDefaultValueDefinition(
                    field_idx + 1,
                    QgsDefaultValue(
                        "ltrim(rtrim(uuid(),'}'),'{')"
                        if table_name == "networks"
                        else "count('{}') + 1".format(table_name)
                    ),
                )

        # --------  Relations
        relation_editors = []
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

            # If we need to, load the target table
            if relation["related_table"] not in layers:
                layers[relation["related_table"]] = QgsVectorLayer(
                    filename + "|layername=" + relation["related_table"],
                    relation["related_table"],
                    "ogr",
                )
                layers[relation["related_table"]].setCustomProperty(
                    "ofdslayer", relation["related_table"]
                )
                if relation["related_table_private"]:
                    layers[relation["related_table"]].setFlags(QgsMapLayer.Private)
                group.insertChildNode(
                    -1, QgsLayerTreeLayer(layers[relation["related_table"]])
                )
                QgsProject.instance().addMapLayer(
                    layers[relation["related_table"]], False
                )

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
            relation_editor = QgsAttributeEditorRelation(join_to_base, None)
            relation_editor.setLabel(relation["title"])
            # set's cardinality option
            relation_editor.setNmRelationId(join_to_related.id())
            relation_editors.append(relation_editor)

        # Set up tabs, if needed
        if relation_editors:
            # Setup
            edit_form_config = layers[table_name].editFormConfig()
            edit_form_config.setLayout(QgsEditFormConfig.TabLayout)

            # Create a tab for all existing fields
            tab_fields = QgsAttributeEditorContainer("Fields", None)
            tab_fields.setType(Qgis.AttributeEditorContainerType.Tab)
            for child in edit_form_config.invisibleRootContainer().children():
                tab_fields.addChildElement(child.clone(None))
            edit_form_config.invisibleRootContainer().clear()
            edit_form_config.invisibleRootContainer().addChildElement(tab_fields)

            # Create a tab for all relations
            tab_relations = QgsAttributeEditorContainer("Relations", None)
            tab_relations.setType(Qgis.AttributeEditorContainerType.Tab)
            for relation_editor in relation_editors:
                tab_relations.addChildElement(relation_editor)
            edit_form_config.invisibleRootContainer().addChildElement(tab_relations)

            # Wrap up
            layers[table_name].setEditFormConfig(edit_form_config)

    # --------  Custom UI
    if custom_ui:
        custom_ui_on_add_handlers = {
            "nodes": plugin.on_node_feature_added,
            "spans": plugin.on_span_feature_added,
        }
        for table_name in custom_ui_on_add_handlers.keys():
            # remove QGIS form on add
            form_config = layers[table_name].editFormConfig()
            form_config.setSuppress(Qgis.AttributeFormSuppression.On)
            layers[table_name].setEditFormConfig(form_config)
            # Add our event handler
            layers[table_name].featureAdded.connect(
                custom_ui_on_add_handlers[table_name]
            )

    # --------   Project Properties
    QgsProject.instance().setTransactionMode(Qgis.TransactionMode.AutomaticGroups)
