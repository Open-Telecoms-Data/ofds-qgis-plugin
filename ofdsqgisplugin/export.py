import copy
import json
import os

from .lib import set_key_in_dict_for_export

PLUGIN_DIR = os.path.dirname(__file__)

START_OF_NETWORK = {
    "nodes": [],
    "spans": [],
    "phases": [],
    "links": {
        "href": "https://raw.githubusercontent.com/Open-Telecoms-Data/open-fibre-data-standard/0__3__0/schema/network-schema.json",
        "rel": "describedby",
    },
    "crs": {
        "name": "urn:ogc:def:crs:OGC::CRS84",
        "uri": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
    },
}


def get_json(layers):
    # Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)
    # Make JSON
    networks = {}
    network_id = None
    # networks first
    for f in layers["networks"].getFeatures():
        network_id = f.attribute("ofds_id")
        # If they put in a network but didn't set an id for it, we'll set one for them
        if not network_id:
            network_id = "network"
        networks[network_id] = copy.deepcopy(START_OF_NETWORK)
        for field_info in schema_information["networks"]["fields"]:
            set_key_in_dict_for_export(
                networks[network_id],
                field_info.get("json_key", field_info["name"]),
                f.attribute(field_info["name"]),
                type=field_info["type"],
            )
    if not network_id:
        network_id = "network"
        networks[network_id] = copy.deepcopy(START_OF_NETWORK)
        networks[network_id]["id"] = network_id
    # phases
    for f in layers["phases"].getFeatures():
        phase_data = {}
        for field_info in schema_information["phases"]["fields"]:
            set_key_in_dict_for_export(
                phase_data,
                field_info.get("json_key", field_info["name"]),
                f.attribute(field_info["name"]),
                type=field_info["type"],
            )
        networks[network_id]["phases"].append(phase_data)
    # nodes
    for f in layers["nodes"].getFeatures():
        node_data = {
            "location": json.loads(f.geometry().asJson()),
        }
        for field_info in schema_information["nodes"]["fields"]:
            set_key_in_dict_for_export(
                node_data,
                field_info.get("json_key", field_info["name"]),
                f.attribute(field_info["name"]),
                type=field_info["type"],
            )
        networks[network_id]["nodes"].append(node_data)
    # spans
    for f in layers["spans"].getFeatures():
        span_data = {
            "route": json.loads(f.geometry().asJson()),
        }
        for field_info in schema_information["spans"]["fields"]:
            set_key_in_dict_for_export(
                span_data,
                field_info.get("json_key", field_info["name"]),
                f.attribute(field_info["name"]),
                type=field_info["type"],
            )
        networks[network_id]["spans"].append(span_data)
    # done
    return {"networks": [v for v in networks.values()]}
