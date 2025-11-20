import copy
import json
import os
import sqlite3
import uuid

from .lib import set_key_in_dict_for_export

PLUGIN_DIR = os.path.dirname(__file__)


START_OF_NETWORK = {
    "nodes": [],
    "spans": [],
    "phases": [],
    "organisations": [],
    "contracts": [],
    "links": {
        "href": "https://raw.githubusercontent.com/Open-Telecoms-Data/open-fibre-data-standard/0__3__0/schema/network-schema.json",
        "rel": "describedby",
    },
    "crs": {
        "name": "urn:ogc:def:crs:OGC::CRS84",
        "uri": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
    },
}


def export_sqlite_to_json(sqlite_filename):
    # Setup
    connection = sqlite3.connect(sqlite_filename)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Start
    def callable(table_name):
        cursor.execute("SELECT * FROM " + table_name)
        return cursor.fetchall()

    data = export_callable_to_json(callable)
    # Wrap up
    connection.commit()
    connection.close()
    return data


def export_callable_to_json(callable):
    # Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "..",
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)
    # Make JSON
    networks = {}
    default_network_id = None
    # Networks first
    for data in callable("networks"):
        default_network_id = data["ofds_id"]
        # If they put in a network but didn't set an id for it, we'll set one for them
        if not default_network_id:
            default_network_id = str(uuid.uuid4())
        networks[default_network_id] = copy.deepcopy(START_OF_NETWORK)
        networks[default_network_id]["id"] = default_network_id
        for column_info in schema_information["tables"]["networks"]["columns"]:
            if column_info["name"] != "ofds_id":
                set_key_in_dict_for_export(
                    networks[default_network_id],
                    column_info["name"],
                    data[column_info["name"]],
                    type=column_info["type"],
                )
    # Other tables
    for table_name in ["nodes", "spans", "phases", "organisations", "contracts"]:
        for data in callable(table_name):
            out = {}
            network_id = data["network_id"] or default_network_id
            out["id"] = data["ofds_id"] or str(uuid.uuid4())
            for column_info in schema_information["tables"][table_name]["columns"]:
                if column_info["name"] not in ["ofds_id", "network_id"]:
                    set_key_in_dict_for_export(
                        out,
                        column_info["name"],
                        data[column_info["name"]],
                        type=column_info["type"],
                    )
            if schema_information["tables"][table_name]["geographic_field"]:
                out[schema_information["tables"][table_name]["geographic_field"]] = (
                    json.loads(data["geom"])
                )
            networks[network_id][table_name].append(out)

    # Wrap up
    return {"networks": [v for v in networks.values()]}
