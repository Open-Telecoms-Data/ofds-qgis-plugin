from qgis.core import (QgsEditorWidgetSetup, QgsLayerTreeLayer, QgsProject,
                       QgsVectorLayer)

from .codelists import (COUNTRY_VALUE_MAP, CURRENCY_VALUE_MAP,
                        MIME_TYPE_VALUE_MAP)


def add_layers(filename):

    # Create a group
    groupName = "Open Fibre"
    root = QgsProject.instance().layerTreeRoot()
    group = root.addGroup(groupName)

    # Add vector Layers
    networks_layer = QgsVectorLayer(filename + "|layername=networks", "Networks", "ogr")
    group.insertChildNode(-1, QgsLayerTreeLayer(networks_layer))
    QgsProject.instance().addMapLayer(networks_layer, False)

    nodes_layer = QgsVectorLayer(filename + "|layername=nodes", "Nodes", "ogr")
    group.insertChildNode(-1, QgsLayerTreeLayer(nodes_layer))
    QgsProject.instance().addMapLayer(nodes_layer, False)

    spans_layer = QgsVectorLayer(filename + "|layername=spans", "Spans", "ogr")
    group.insertChildNode(-1, QgsLayerTreeLayer(spans_layer))
    QgsProject.instance().addMapLayer(spans_layer, False)

    contracts_layer = QgsVectorLayer(
        filename + "|layername=contracts", "contracts", "ogr"
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(contracts_layer))
    QgsProject.instance().addMapLayer(contracts_layer, False)

    phases_layer = QgsVectorLayer(filename + "|layername=phases", "Phases", "ogr")
    group.insertChildNode(-1, QgsLayerTreeLayer(phases_layer))
    QgsProject.instance().addMapLayer(phases_layer, False)

    spans_networkProviders_layer = QgsVectorLayer(
        filename + "|layername=spans_networkProviders",
        "spans_networkProviders",
        "ogr",
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(spans_networkProviders_layer))
    QgsProject.instance().addMapLayer(spans_networkProviders_layer, False)

    phases_funders_layer = QgsVectorLayer(
        filename + "|layername=phases_funders", "phases_funders", "ogr"
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(phases_funders_layer))
    QgsProject.instance().addMapLayer(phases_funders_layer, False)

    organisations_layer = QgsVectorLayer(
        filename + "|layername=organisations", "organisations", "ogr"
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(organisations_layer))

    nodes_networkProviders_layer = QgsVectorLayer(
        filename + "|layername=nodes_networkProviders",
        "nodes_networkProviders",
        "ogr",
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(nodes_networkProviders_layer))
    QgsProject.instance().addMapLayer(nodes_networkProviders_layer, False)

    nodes_internationalConnections_layer = QgsVectorLayer(
        filename + "|layername=nodes_internationalConnections",
        "nodes_internationalConnections",
        "ogr",
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(nodes_internationalConnections_layer))
    QgsProject.instance().addMapLayer(nodes_internationalConnections_layer, False)

    links_layer = QgsVectorLayer(filename + "|layername=links", "links", "ogr")
    group.insertChildNode(-1, QgsLayerTreeLayer(links_layer))
    QgsProject.instance().addMapLayer(links_layer, False)

    contracts_relatedPhases_layer = QgsVectorLayer(
        filename + "|layername=contracts_relatedPhases",
        "contracts_relatedPhases",
        "ogr",
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(contracts_relatedPhases_layer))
    QgsProject.instance().addMapLayer(contracts_relatedPhases_layer, False)

    contracts_documents_layer = QgsVectorLayer(
        filename + "|layername=contracts_documents", "contracts_documents", "ogr"
    )
    group.insertChildNode(-1, QgsLayerTreeLayer(contracts_documents_layer))
    QgsProject.instance().addMapLayer(contracts_documents_layer, False)

    # Configure layer fields
    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (1, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (3, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (4, "TextEdit", {}),
        (5, "TextEdit", {}),
        (6, "TextEdit", {}),
        (7, "TextEdit", {}),
        (8, "TextEdit", {}),
        (9, "TextEdit", {}),
        (10, "TextEdit", {}),
        (11, "TextEdit", {}),
        (12, "TextEdit", {}),
        (13, "TextEdit", {}),
        (14, "TextEdit", {}),
        (15, "TextEdit", {}),
        (16, "TextEdit", {}),
        (17, "TextEdit", {}),
        (18, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (19, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (20, "TextEdit", {}),
        (21, "TextEdit", {}),
        (22, "TextEdit", {}),
        (23, "TextEdit", {}),
    ]:
        networks_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))

    for idx, type, config in [
        (0, "Hidden", {}),
        (1, "UuidGenerator", {}),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            3,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "phases/0/id",
                "Layer": phases_layer.id(),
                "LayerName": "phases",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=phases",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "phases/0/name",
            },
        ),
        (
            4,
            "ValueMap",
            {
                "map": [
                    {"Decommissioned": "decommissioned"},
                    {"Inactive": "inactive"},
                    {"Operational": "operational"},
                    {"Planned": "planned"},
                    {"Proposed": "proposed"},
                    {"Under construction": "underConstruction"},
                ]
            },
        ),
        (5, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (6, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (7, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (8, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (9, "ValueMap", {"map": COUNTRY_VALUE_MAP}),
        (
            10,
            "ValueMap",
            {
                "map": [
                    {"Add drop site": "addDropSite"},
                    {"Aggregation point": "aggregationPoint"},
                    {"Border crossing": "borderCrossing"},
                    {"Cabinet": "cabinet"},
                    {"Cable landing point": "cableLanding"},
                    {"Data centre": "dataCentre"},
                    {"Exchange": "exchange"},
                    {"Internet Exchange Point": "ixp"},
                    {"Point of Presence": "pop"},
                    {"Repeater site": "repeaterSite"},
                    {"Substation": "substation"},
                    {"Tower": "tower"},
                ]
            },
        ),
        (11, "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}),
        (12, "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}),
        (
            13,
            "ValueMap",
            {
                "map": [
                    {"Internet Protocol": "ip"},
                    {"Multi-Protocol Label Switching": "mpls"},
                ]
            },
        ),
        (
            14,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (
            15,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (16, "Hidden", {}),
        (17, "Hidden", {}),
        (18, "Hidden", {}),
        (19, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            20,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (21, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
    ]:
        nodes_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (1, "UuidGenerator", {}),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            3,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "phases/0/id",
                "Layer": phases_layer.id(),
                "LayerName": "phases",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=phases",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "phases/0/name",
            },
        ),
        (
            4,
            "ValueMap",
            {
                "map": [
                    {"Decommissioned": "decommissioned"},
                    {"Inactive": "inactive"},
                    {"Operational": "operational"},
                    {"Planned": "planned"},
                    {"Proposed": "proposed"},
                    {"Under construction": "underConstruction"},
                ]
            },
        ),
        (
            5,
            "DateTime",
            {
                "allow_null": True,
                "calendar_popup": True,
                "display_format": "yyyy-MM-dd",
                "field_format": "yyyy-MM-dd",
                "field_iso_format": False,
            },
        ),
        (
            6,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "nodes/0/id",
                "Layer": nodes_layer.id(),
                "LayerName": "nodes",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=nodes",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "nodes/0/name",
            },
        ),
        (
            7,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "nodes/0/id",
                "Layer": nodes_layer.id(),
                "LayerName": "nodes",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=nodes",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "nodes/0/name",
            },
        ),
        (8, "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}),
        (
            9,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (
            10,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (
            11,
            "ValueMap",
            {
                "map": [
                    {"Coaxial cable": "coaxial"},
                    {"Copper wire": "copper"},
                    {"Fibre optic cable": "fibre"},
                    {"Microwave radio": "microwave"},
                ]
            },
        ),
        (
            12,
            "ValueMap",
            {
                "map": [
                    {"Above ground": "aboveGround"},
                    {"Below ground": "belowGround"},
                ]
            },
        ),
        (13, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (14, "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}),
        (
            15,
            "ValueMap",
            {
                "map": [
                    {"G.651.1": "G.651.1"},
                    {"G.652": "G.652"},
                    {"G.653": "G.653"},
                    {"G.654": "G.654"},
                    {"G.655": "G.655"},
                    {"G.656": "G.656"},
                    {"G.657": "G.657"},
                ]
            },
        ),
        (16, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (17, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (18, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (19, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            20,
            "ValueMap",
            {
                "map": [
                    {"Dense Wavelength Division Multiplexing": "dwdm"},
                    {"Synchronous Digital Hierarchy": "sdh"},
                    {"Synchronous Optical Networking": "sonet"},
                    {"Time Division Multiplexing": "tdm"},
                ]
            },
        ),
        (21, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (22, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (23, "ValueMap", {"map": COUNTRY_VALUE_MAP}),
        (
            24,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": True,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (25, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (26, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (27, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (28, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (29, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            30,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (31, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
    ]:
        spans_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (1, "UuidGenerator", {}),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (3, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            4,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
    ]:
        phases_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            1,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (
            2,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "spans/0/id",
                "Layer": spans_layer.id(),
                "LayerName": "spans",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=spans",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "spans/0/name",
            },
        ),
        (
            3,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (4, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
    ]:
        spans_networkProviders_layer.setEditorWidgetSetup(
            idx, QgsEditorWidgetSetup(type, config)
        )

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            1,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (
            2,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "phases/0/id",
                "Layer": phases_layer.id(),
                "LayerName": "phases",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=phases",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "phases/0/name",
            },
        ),
        (
            3,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (4, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
    ]:
        phases_funders_layer.setEditorWidgetSetup(
            idx, QgsEditorWidgetSetup(type, config)
        )

    QgsProject.instance().addMapLayer(organisations_layer, False)
    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (1, "UuidGenerator", {}),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (3, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (4, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (5, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (6, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (7, "ValueMap", {"map": COUNTRY_VALUE_MAP}),
        (
            8,
            "ValueMap",
            {
                "map": [
                    {
                        "Physical infrastructure provider": "physicalInfrastructureProvider"
                    },
                    {"Network provider": "networkProvider"},
                    {"Supplier": "supplier"},
                    {"Funder": "funder"},
                ]
            },
        ),
        (9, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (10, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (11, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            12,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
    ]:
        organisations_layer.setEditorWidgetSetup(
            idx, QgsEditorWidgetSetup(type, config)
        )

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            1,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (
            2,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "nodes/0/id",
                "Layer": nodes_layer.id(),
                "LayerName": "nodes",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=nodes",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "nodes/0/name",
            },
        ),
        (
            3,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "organisations/0/id",
                "Layer": organisations_layer.id(),
                "LayerName": "organisations",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=organisations",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "organisations/0/name",
            },
        ),
        (4, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
    ]:
        nodes_networkProviders_layer.setEditorWidgetSetup(
            idx, QgsEditorWidgetSetup(type, config)
        )

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            1,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (
            2,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "nodes/0/id",
                "Layer": nodes_layer.id(),
                "LayerName": "nodes",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=nodes",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "nodes/0/name",
            },
        ),
        (3, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (4, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (5, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (6, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (7, "ValueMap", {"map": COUNTRY_VALUE_MAP}),
    ]:
        nodes_internationalConnections_layer.setEditorWidgetSetup(
            idx, QgsEditorWidgetSetup(type, config)
        )

    # Links_layer
    # No editor widget setups?
    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            1,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (
            2,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "contracts/0/id",
                "Layer": contracts_layer.id(),
                "LayerName": "contracts",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=contracts",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "contracts/0/title",
            },
        ),
        (
            3,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "phases/0/id",
                "Layer": phases_layer.id(),
                "LayerName": "phases",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=phases",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "phases/0/name",
            },
        ),
        (4, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
    ]:
        contracts_relatedPhases_layer.setEditorWidgetSetup(
            idx, QgsEditorWidgetSetup(type, config)
        )

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            1,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
        (
            2,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "contracts/0/id",
                "Layer": contracts_layer.id(),
                "LayerName": "contracts",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=contracts",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "contracts/0/title",
            },
        ),
        (3, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (4, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (5, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            6,
            "ValueMap",
            {"map": MIME_TYPE_VALUE_MAP},
        ),
    ]:
        contracts_documents_layer.setEditorWidgetSetup(
            idx, QgsEditorWidgetSetup(type, config)
        )

    for idx, type, config in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (1, "UuidGenerator", {}),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (3, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            4,
            "ValueMap",
            {
                "map": [
                    {"Public Private Partnership (PPP)": "ppp"},
                    {"Private": "private"},
                    {"Public": "public"},
                ]
            },
        ),
        (5, "TextEdit", {"IsMultiline": False, "UseHtml": False}),
        (
            6,
            "ValueMap",
            {"map": CURRENCY_VALUE_MAP},
        ),
        (
            7,
            "DateTime",
            {
                "allow_null": True,
                "calendar_popup": True,
                "display_format": "yyyy-MM-dd",
                "field_format": "yyyy-MM-dd",
                "field_iso_format": False,
            },
        ),
        (
            8,
            "ValueRelation",
            {
                "AllowMulti": False,
                "AllowNull": False,
                "Description": None,
                "FilterExpression": None,
                "Key": "id",
                "Layer": networks_layer.id(),
                "LayerName": "networks",
                "LayerProviderName": "ogr",
                "LayerSource": filename + "|layername=networks",
                "NofColumns": 1,
                "OrderByValue": False,
                "UseCompleter": False,
                "Value": "name",
            },
        ),
    ]:
        contracts_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))
