import csv
import json
import os

from qgis.core import (Qgis, QgsAttributeEditorContainer,
                       QgsAttributeEditorRelation, QgsDefaultValue,
                       QgsEditFormConfig, QgsEditorWidgetSetup,
                       QgsLayerTreeLayer, QgsMapLayer, QgsProject, QgsRelation,
                       QgsVectorLayer, QgsLayerTreeGroup, QgsUnitTypes,
                       QgsMarkerSymbol, QgsSymbol, QgsLineSymbol,
                       QgsSnappingConfig, QgsTolerance,
                       QgsPalLayerSettings, QgsVectorLayerSimpleLabeling,
                       QgsTextFormat, QgsTextBufferSettings)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import Qt

PLUGIN_DIR = os.path.dirname(__file__)


def ensure_layer_order(root=None, ofds_group=None, is_initial_creation=False):
    """Ensure OFDS layers are above basemaps and nodes are above spans.
    
    This function:
    1. Within the Open Fibre group, ensures nodes layer is above spans layer
    2. Moves the Open Fibre group to the top
    3. Moves raster/basemap layers to the bottom of the layer tree
    
    Args:
        root: QgsLayerTreeGroup - the root of the layer tree (optional)
        ofds_group: QgsLayerTreeGroup - the Open Fibre group (optional)
        is_initial_creation: bool - if True, we're being called during add_layers
                            and should not clone/move the group (layers are still being added)
    """
    if root is None:
        root = QgsProject.instance().layerTreeRoot()
    
    # Find the Open Fibre group if not provided
    if ofds_group is None:
        for child in root.children():
            if isinstance(child, QgsLayerTreeGroup) and child.name() == "Open Fibre":
                ofds_group = child
                break
    
    if not ofds_group:
        return
    
    # During initial creation, we cannot move the group because:
    # 1. Layers are still being added to it
    # 2. Cloning would lose those layer references
    # The group is already at the top when newly created, so we just need to
    # ensure nodes is above spans (if they exist yet)
    if is_initial_creation:
        _order_ofds_layers_in_group(ofds_group)
        return
    
    # For calls after initial creation (e.g., when a new basemap is added):
    # Step 1: Within OFDS group, ensure nodes is above spans
    _order_ofds_layers_in_group(ofds_group)
    
    # Step 2: Ensure Open Fibre group is at the top
    children = root.children()
    if children and children[0] != ofds_group:
        clone = ofds_group.clone()
        root.removeChildNode(ofds_group)
        root.insertChildNode(0, clone)
    
    # Step 3: Move rasters to bottom
    _move_rasters_to_bottom(root)


def _move_group_to_top(root, group):
    """Move a group to the top of the layer tree (index 0)."""
    children = root.children()
    if not children or children[0] == group:
        return  # Already at top
    
    # Find current index
    current_index = -1
    for i, child in enumerate(children):
        if child == group:
            current_index = i
            break
    
    if current_index > 0:
        # Use clone approach for moving groups
        clone = group.clone()
        root.removeChildNode(group)
        root.insertChildNode(0, clone)


def _move_rasters_to_bottom(root):
    """Move all raster layers to the bottom of the layer tree."""
    children = root.children()
    raster_indices = []
    
    # Find all raster layer indices
    for i, child in enumerate(children):
        if isinstance(child, QgsLayerTreeLayer):
            layer = child.layer()
            if layer and layer.type() == QgsMapLayer.RasterLayer:
                raster_indices.append(i)
    
    # Move each raster to the bottom (process in reverse to maintain order)
    for idx in reversed(raster_indices):
        child = root.children()[idx]
        clone = child.clone()
        root.removeChildNode(child)
        root.addChildNode(clone)


def _order_ofds_layers_in_group(group):
    """Order layers within the Open Fibre group: nodes above spans.
    
    Uses a simple approach: just ensure 'nodes' is above 'spans'.
    Does not remove/re-add all layers to avoid losing layer references.
    """
    children = group.children()
    if len(children) < 2:
        return
    
    # Find nodes and spans indices
    nodes_index = -1
    spans_index = -1
    
    for i, child in enumerate(children):
        if isinstance(child, QgsLayerTreeLayer):
            layer = child.layer()
            if layer:
                layer_name = layer.customProperty("ofdslayer", "")
                if layer_name == "nodes":
                    nodes_index = i
                elif layer_name == "spans":
                    spans_index = i
    
    # If spans is above nodes, swap them
    if nodes_index >= 0 and spans_index >= 0 and spans_index < nodes_index:
        # Move nodes to be above spans
        nodes_node = children[nodes_index]
        clone = nodes_node.clone()
        group.removeChildNode(nodes_node)
        group.insertChildNode(spans_index, clone)


def move_basemap_to_bottom(layer):
    """Move a specific basemap/raster layer to the bottom of the layer tree.
    
    This is called when a new layer is added to ensure basemaps stay at bottom.
    
    Args:
        layer: QgsMapLayer - the layer to check and potentially move
    """
    if not layer or layer.type() != QgsMapLayer.RasterLayer:
        return
    
    root = QgsProject.instance().layerTreeRoot()
    
    # Find the layer node in the tree
    layer_node = root.findLayer(layer.id())
    if not layer_node:
        return
    
    # Only move if it's a direct child of root (not in a group)
    parent = layer_node.parent()
    if parent == root:
        # Clone, remove, and re-add at the end (bottom)
        clone = layer_node.clone()
        root.removeChildNode(layer_node)
        root.addChildNode(clone)
        
        # Also ensure OFDS group stays at top
        for child in root.children():
            if isinstance(child, QgsLayerTreeGroup) and child.name() == "Open Fibre":
                if root.children()[0] != child:
                    clone = child.clone()
                    root.removeChildNode(child)
                    root.insertChildNode(0, clone)
                break


def configure_labeling(layer, label_field, layer_type):
    """Configure automatic labeling for a layer.
    
    Sets up labels with a readable style including text buffer (halo)
    for visibility against various backgrounds.
    
    Args:
        layer: QgsVectorLayer to configure labeling for
        label_field: Name of the field to use for labels (e.g., 'name')
        layer_type: Either 'point' or 'line' for placement settings
    """
    # Create label settings
    label_settings = QgsPalLayerSettings()
    label_settings.fieldName = label_field
    label_settings.enabled = True
    
    # Text format
    text_format = QgsTextFormat()
    text_format.setSize(9)
    text_format.setColor(QColor(0, 0, 0))  # Black text
    
    # Set font
    font = QFont()
    font.setFamily("Arial")
    font.setBold(False)
    text_format.setFont(font)
    
    # Add buffer (halo) for readability against any background
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(1.0)
    buffer_settings.setColor(QColor(255, 255, 255))  # White buffer
    buffer_settings.setOpacity(0.8)
    text_format.setBuffer(buffer_settings)
    
    label_settings.setFormat(text_format)
    
    # Placement settings based on layer type
    # QGIS 3.26+ uses Qgis.LabelPlacement enum
    if layer_type == 'point':
        # For points: place label around the point
        label_settings.placement = Qgis.LabelPlacement.AroundPoint
        # Offset from point
        label_settings.xOffset = 2.0
        label_settings.yOffset = -1.0
    else:
        # For lines: curved labels following the line
        label_settings.placement = Qgis.LabelPlacement.Curved
        # Repeat labels along long lines
        label_settings.repeatDistance = 300
    
    # Apply labeling to layer
    labeling = QgsVectorLayerSimpleLabeling(label_settings)
    layer.setLabeling(labeling)
    layer.setLabelsEnabled(True)


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

    # --------   Create a group at the TOP of the layer tree
    groupName = "Open Fibre"
    root = QgsProject.instance().layerTreeRoot()
    group = root.insertGroup(0, groupName)  # Insert at index 0 (top)

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
            # Create a visible line symbol for spans
            # Width in MM so it scales with zoom (stays visible at continent level)
            line_symbol = QgsLineSymbol.createSimple({
                'color': '255,127,0,255',        # Orange color
                'width': '0.8',                  # Width in millimeters
                'width_unit': 'MM',              # Screen units - scales with zoom
                'capstyle': 'round',             # Round line caps
                'joinstyle': 'round'             # Round line joins
            })
            
            # Ensure width is in MM for zoom-dependent rendering
            symbol_layer = line_symbol.symbolLayer(0)
            symbol_layer.setWidth(0.8)
            symbol_layer.setWidthUnit(QgsUnitTypes.RenderMillimeters)
            
            # Set pen cap and join styles for smooth lines
            symbol_layer.setPenCapStyle(Qt.RoundCap)
            symbol_layer.setPenJoinStyle(Qt.RoundJoin)
            
            # Apply the symbol to the layer
            layers[table_name].renderer().setSymbol(line_symbol)
            
            # Configure labeling for spans
            configure_labeling(layers[table_name], 'name', 'line')
        
        # Node symbology - larger, more visible markers with fixed size
        elif table_info["geographic_type"] == "POINT":
            # Create a visible marker symbol
            # Size in MM so it scales with zoom (stays visible at continent level)
            marker = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': '0,120,215,255',       # Blue fill
                'size': '3.0',                   # Size in millimeters
                'size_unit': 'MM',               # Screen units - scales with zoom
                'outline_color': '35,35,35,255', # Dark gray outline
                'outline_width': '0.4',          # Outline width in MM
                'outline_width_unit': 'MM'       # Outline in MM too
            })
            
            # Ensure size is in MM for zoom-dependent rendering
            symbol_layer = marker.symbolLayer(0)
            symbol_layer.setSizeUnit(QgsUnitTypes.RenderMillimeters)
            symbol_layer.setStrokeWidthUnit(QgsUnitTypes.RenderMillimeters)
            
            # Apply the symbol to the layer
            layers[table_name].renderer().setSymbol(marker)
            
            # Configure labeling for nodes
            configure_labeling(layers[table_name], 'name', 'point')
        
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
    
    # --------   Ensure proper layer ordering
    # During initial creation, only order nodes above spans within the group
    # Don't move the group itself (it's already at top and moving would lose layer references)
    ensure_layer_order(root, group, is_initial_creation=True)
    
    # --------   Configure snapping for OFDS layers
    # Enable snapping so spans can easily connect to node centers
    configure_snapping_for_ofds(layers)


def configure_snapping_for_ofds(layers):
    """Configure snapping for OFDS layers so spans connect to node centers.
    
    This sets up:
    - Global snapping enabled
    - Advanced configuration mode for per-layer settings
    - Nodes layer: snap to vertices (node centers)
    - Spans layer: snap to vertices (endpoints)
    - Topological editing enabled
    
    Args:
        layers: dict of layer name -> QgsVectorLayer
    """
    project = QgsProject.instance()
    config = project.snappingConfig()
    
    # Enable snapping globally
    config.setEnabled(True)
    
    # Use advanced configuration for per-layer settings
    config.setMode(QgsSnappingConfig.AdvancedConfiguration)
    
    # Configure snapping for nodes layer (snap to vertices = node centers)
    if 'nodes' in layers:
        individual_config = QgsSnappingConfig.IndividualLayerSettings(
            True,                              # enabled
            QgsSnappingConfig.VertexAndSegment,  # type - snap to vertices and segments
            10,                                # tolerance
            QgsTolerance.Pixels                # units
        )
        config.setIndividualLayerSettings(
            layers['nodes'],
            individual_config
        )
    
    # Configure snapping for spans (snap to endpoints/vertices)
    if 'spans' in layers:
        individual_config = QgsSnappingConfig.IndividualLayerSettings(
            True,                          # enabled
            QgsSnappingConfig.Vertex,      # type - snap to vertices only
            10,                            # tolerance
            QgsTolerance.Pixels            # units
        )
        config.setIndividualLayerSettings(
            layers['spans'],
            individual_config
        )
    
    # Apply the snapping configuration
    project.setSnappingConfig(config)
    
    # Enable topological editing for maintaining connected geometries
    project.setTopologicalEditing(True)
