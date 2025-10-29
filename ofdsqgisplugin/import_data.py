import json

from qgis.core import QgsFeature, QgsJsonUtils


def import_json(layers, data):
    LAYERS_TO_EDIT = ["networks", "nodes", "spans"]
    # Start
    for layer_id in LAYERS_TO_EDIT:
        layers[layer_id].startEditing()
    # Network
    networks = data.get("networks", [])
    if isinstance(networks, list):
        for network in networks:
            network_feature = QgsFeature(layers["networks"].fields())
            network_feature.setAttribute("id", network.get("id"))
            network_feature.setAttribute("name", network.get("name"))
            if not layers["networks"].addFeature(network_feature):
                raise Exception("Could not add to networks layer")
            # Nodes
            nodes = network.get("nodes", [])
            if isinstance(nodes, list):
                for node in nodes:
                    node_feature = QgsFeature(layers["nodes"].fields())
                    node_feature.setAttribute("nodes/0/id", node.get("id"))
                    node_feature.setAttribute("nodes/0/name", node.get("name"))
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
                    span_feature.setAttribute("spans/0/id", span.get("id"))
                    span_feature.setAttribute("spans/0/name", span.get("name"))
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
