import json
import os
import uuid

from qgis.core import QgsFeature, QgsJsonUtils

from .lib import get_deep_key_from_data_for_import

PLUGIN_DIR = os.path.dirname(__file__)


def import_json(layers, data):
    # Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)
    # Setup
    LAYERS_TO_EDIT = [
        "networks",
        "nodes",
        "spans",
        "phases",
        "contracts",
        "organisations",
    ]
    # Start
    for layer_id in LAYERS_TO_EDIT:
        layers[layer_id].startEditing()
    # Network
    networks = data.get("networks", [])
    if isinstance(networks, list):
        for network in networks:
            network_feature = QgsFeature(layers["networks"].fields())
            network_id = network.get("id") or str(uuid.uuid4())
            network_feature.setAttribute("ofds_id", network_id)
            for field_info in schema_information["networks"]["fields"]:
                if field_info["name"] != "ofds_id":
                    network_feature.setAttribute(
                        field_info["name"],
                        get_deep_key_from_data_for_import(
                            network, field_info.get("json_key", field_info["name"])
                        ),
                    )
            if not layers["networks"].addFeature(network_feature):
                raise Exception("Could not add to networks layer")
            # phases, contracts, organisations
            for table in ["phases", "contracts", "organisations"]:
                datas = network.get(table, [])
                if isinstance(datas, list):
                    for data in datas:
                        feature = QgsFeature(layers[table].fields())
                        feature.setAttribute("network_id", network_id)
                        for field_info in schema_information[table]["fields"]:
                            if field_info["name"] != "network_id":
                                feature.setAttribute(
                                    field_info["name"],
                                    get_deep_key_from_data_for_import(
                                        data,
                                        field_info.get("json_key", field_info["name"]),
                                    ),
                                )
                        if not layers[table].addFeature(feature):
                            raise Exception("Could not add to {} layer".format(table))
            # Nodes
            nodes = network.get("nodes", [])
            if isinstance(nodes, list):
                for node in nodes:
                    node_feature = QgsFeature(layers["nodes"].fields())
                    node_feature.setAttribute("network_id", network_id)
                    for field_info in schema_information["nodes"]["fields"]:
                        if field_info["name"] != "network_id":
                            node_feature.setAttribute(
                                field_info["name"],
                                get_deep_key_from_data_for_import(
                                    node, field_info.get("json_key", field_info["name"])
                                ),
                            )
                    node_feature.setGeometry(
                        QgsJsonUtils.geometryFromGeoJson(
                            json.dumps(node.get("location", "{}"))
                        )
                    )
                    if not layers["nodes"].addFeature(node_feature):
                        raise Exception("Could not add to nodes layer")
            # Spans
            spans = network.get("spans", [])
            if isinstance(spans, list):
                for span in spans:
                    span_feature = QgsFeature(layers["spans"].fields())
                    span_feature.setAttribute("network_id", network_id)
                    for field_info in schema_information["spans"]["fields"]:
                        if field_info["name"] != "network_id":
                            span_feature.setAttribute(
                                field_info["name"],
                                get_deep_key_from_data_for_import(
                                    span, field_info.get("json_key", field_info["name"])
                                ),
                            )
                    span_feature.setGeometry(
                        QgsJsonUtils.geometryFromGeoJson(
                            json.dumps(span.get("route", "{}"))
                        )
                    )
                    if not layers["spans"].addFeature(span_feature):
                        raise Exception("Could not add to spans layer")
    # Commit
    for layer_id in LAYERS_TO_EDIT:
        if not layers[layer_id].commitChanges():
            raise Exception("Could not commit {} layer".format(layer_id))
