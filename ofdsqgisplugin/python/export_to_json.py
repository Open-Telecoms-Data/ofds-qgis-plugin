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
    "links": [
        {
            "href": "https://raw.githubusercontent.com/Open-Telecoms-Data/open-fibre-data-standard/0__3__0/schema/network-schema.json",
            "rel": "describedby",
        }
    ],
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
                    column_info["name"].replace("__", "/"),
                    data[column_info["name"]],
                    type=column_info["type"],
                )
    # If they didn't set any networks, we'll create one, as we need it!
    if not default_network_id:
        default_network_id = str(uuid.uuid4())
        networks[default_network_id] = copy.deepcopy(START_OF_NETWORK)
        networks[default_network_id]["id"] = default_network_id
    # Other tables - first load geopackage id's to json id mapping
    geopackage_id_to_standard_info_mappings = {}
    for table_name in ["nodes", "spans", "phases", "organisations", "contracts"]:
        geopackage_id_to_standard_info_mappings[table_name] = {}
        for data in callable(table_name):
            geopackage_id_to_standard_info_mappings[table_name][data["id"]] = {
                "id": data["ofds_id"]
            }
    # Other tables - now process
    for table_name, sub_tables in [
        ("nodes", [("internationalConnections", "node_id")]),
        ("spans", []),
        ("phases", []),
        ("organisations", []),
        ("contracts", [("documents", "contract_id")]),
    ]:
        for data in callable(table_name):
            out = {}
            network_id = data["network_id"] or default_network_id
            # Normal fields
            out["id"] = data["ofds_id"] or str(uuid.uuid4())
            for column_info in schema_information["tables"][table_name]["columns"]:
                if column_info["name"] not in ["ofds_id", "network_id"]:
                    set_key_in_dict_for_export(
                        out,
                        column_info["name"].replace("__", "/"),
                        data[column_info["name"]],
                        type=column_info["type"],
                    )
            if schema_information["tables"][table_name]["geographic_field"]:
                out[schema_information["tables"][table_name]["geographic_field"]] = (
                    json.loads(data["geom"])
                )
            # other tables
            # This is an inefficient way of doing this, as we loop within loop - but will do for first pass and the small data sizes we expect
            for sub_table_and_field_name, parent_field_name in sub_tables:
                sub_values = []
                for sub_table_data in callable(
                    table_name + "_" + sub_table_and_field_name
                ):
                    if (
                        sub_table_data[parent_field_name] == out["id"]
                        and sub_table_data["network_id"] == network_id
                    ):
                        sub_out = {}
                        for column_info in schema_information["tables"][
                            table_name + "_" + sub_table_and_field_name
                        ]["columns"]:
                            if column_info["name"] not in [
                                parent_field_name,
                                "network_id",
                            ]:
                                set_key_in_dict_for_export(
                                    sub_out,
                                    column_info["name"].replace("__", "/"),
                                    sub_table_data[column_info["name"]],
                                    type=column_info["type"],
                                )
                        sub_values.append(sub_out)
                if sub_values:
                    out[sub_table_and_field_name] = sub_values

            # relations
            # This is an inefficient way of doing this, as we loop within loop - but will do for first pass and the small data sizes we expect
            for relation in schema_information["tables"][table_name].get(
                "relations", []
            ):
                # First, for codelist, we may have to load the codelist contents
                if (
                    relation.get("codelist")
                    and relation["related_table"]
                    not in geopackage_id_to_standard_info_mappings
                ):
                    geopackage_id_to_standard_info_mappings[
                        relation["related_table"]
                    ] = {}
                    for related_data in callable(relation["related_table"]):
                        geopackage_id_to_standard_info_mappings[
                            relation["related_table"]
                        ][related_data["id"]] = related_data["code"]

                # Now process
                values = []
                for relation_data in callable(relation["mapping_table"]):
                    # We convert relation_data columns to ints as currently it's text column types ... if they become int column types later we can remove this
                    if int(relation_data["base_id"]) == data["id"]:
                        values.append(
                            geopackage_id_to_standard_info_mappings[
                                relation["related_table"]
                            ][int(relation_data["related_id"])]
                        )
                if values:
                    out[relation["standard_field"]] = values
            # wrap up
            networks[network_id][table_name].append(out)

    # Clear empty arrays out of networks
    for network in networks.values():
        for key in ["nodes", "spans", "phases", "organisations", "contracts"]:
            if not network[key]:
                del network[key]
    # Wrap up
    return {"networks": [v for v in networks.values()]}
