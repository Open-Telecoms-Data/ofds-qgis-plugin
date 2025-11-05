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

    # Symbology
    renderer = spans_layer.renderer()
    symbol = renderer.symbol()
    symbol.setWidth(1.5)
    # spans_layer.triggerRepaint() may be needed, but as this point there is no data to repaint

    # Configure layer fields
    for idx, type, config, alias in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
        (1, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Name"),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Website"),
        (3, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Publisher ID"),
        (4, "TextEdit", {}, "Publisher Name"),
        (5, "TextEdit", {}, "Publisher Identifier ID"),
        (6, "TextEdit", {}, "Publisher Identifier Scheme"),
        (7, "TextEdit", {}, "Publisher Identifier Legal Name"),
        (8, "TextEdit", {}, "Publisher Identifier URI"),
        (9, "TextEdit", {}, "Publisher Country"),
        (10, "TextEdit", {}, "Publisher Roles"),
        (11, "TextEdit", {}, "Publisher Role Details"),
        (12, "TextEdit", {}, "Publisher Website"),
        (13, "TextEdit", {}, "Publisher Logo"),
        (14, "TextEdit", {}, "Publication Date"),
        (15, "TextEdit", {}, "Collection Date"),
        (16, "TextEdit", {}, "Accuracy"),
        (17, "TextEdit", {}, "Accuracy Details"),
        (18, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Language"),
        (19, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Id"),
        (20, "TextEdit", {}, None),
        (21, "TextEdit", {}, None),
        (22, "TextEdit", {}, None),
        (23, "TextEdit", {}, None),
    ]:
        networks_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))
        if alias:
            networks_layer.setFieldAlias(idx, alias)

    for idx, type, config, alias in [
        (0, "Hidden", {}, None),
        (1, "UuidGenerator", {}, "Id"),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Name"),
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
            "Phase",
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
            "Status",
        ),
        (5, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Address Street"),
        (6, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Address Locality"),
        (7, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Address Region"),
        (
            8,
            "TextEdit",
            {"IsMultiline": False, "UseHtml": False},
            "Address Postal Code",
        ),
        (9, "ValueMap", {"map": COUNTRY_VALUE_MAP}, "Address Country"),
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
            "Type",
        ),
        (
            11,
            "ValueMap",
            {"map": [{"True": "true"}, {"False": "false"}]},
            "Access Point",
        ),
        (12, "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}, "Power"),
        (
            13,
            "ValueMap",
            {
                "map": [
                    {"Internet Protocol": "ip"},
                    {"Multi-Protocol Label Switching": "mpls"},
                ]
            },
            "Technologies",
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
            "Physical Infrastructure Provider",
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
            "Network Providers",
        ),
        (16, "Hidden", {}, None),
        (17, "Hidden", {}, None),
        (18, "Hidden", {}, None),
        (19, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
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
            None,
        ),
        (21, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
    ]:
        nodes_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))
        if alias:
            nodes_layer.setFieldAlias(idx, alias)

    for idx, type, config, alias in [
        (0, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
        (1, "UuidGenerator", {}, "Id"),
        (2, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Name"),
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
            "Phase",
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
            "Status",
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
            "Ready for service date",
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
            "Start Node",
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
            "End Node",
        ),
        (8, "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}, "Directed"),
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
            "Physical Infrastructure Provider",
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
            "Supplier",
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
            "Transmission Medium",
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
            "Deployment",
        ),
        (
            13,
            "TextEdit",
            {"IsMultiline": False, "UseHtml": False},
            "Deployment Details",
        ),
        (14, "ValueMap", {"map": [{"True": "true"}, {"False": "false"}]}, "Dark Fibre"),
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
            "Fibre Type",
        ),
        (
            16,
            "TextEdit",
            {"IsMultiline": False, "UseHtml": False},
            "Fibre Type Subtype",
        ),
        (
            17,
            "TextEdit",
            {"IsMultiline": False, "UseHtml": False},
            "Fibre Type Details",
        ),
        (18, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Fibre Count"),
        (19, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Fibre Length"),
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
            "Technologies",
        ),
        (21, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Capacity"),
        (22, "TextEdit", {"IsMultiline": False, "UseHtml": False}, "Capacity Details"),
        (23, "ValueMap", {"map": COUNTRY_VALUE_MAP}, "Countries"),
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
            "Network Providers",
        ),
        (25, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
        (26, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
        (27, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
        (28, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
        (29, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
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
            None,
        ),
        (31, "TextEdit", {"IsMultiline": False, "UseHtml": False}, None),
    ]:
        spans_layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup(type, config))
        if alias:
            spans_layer.setFieldAlias(idx, alias)

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
