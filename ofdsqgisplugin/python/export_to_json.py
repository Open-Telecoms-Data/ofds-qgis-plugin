import copy
import json
import os
import sqlite3
import uuid

PLUGIN_DIR = os.path.dirname(__file__)


START_OF_NETWORK = {
    "nodes": [],
    "spans": [],
    "phases": [],
    "organisations": [],
    "contracts": [],
    "wayleaves": [],
    "links": [
        {
            "href": "https://raw.githubusercontent.com/Open-Telecoms-Data/open-fibre-data-standard/0__4__0/schema/network-schema.json",
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

    data = ExportCallableToJSON(callable).go()
    # Wrap up
    connection.commit()
    connection.close()
    return data


class ExportCallableToJSON:

    def __init__(self, callable):
        self._callable = callable
        self._tables_ids_to_standard_info_mappings = {}
        # Get Information
        with open(
            os.path.join(
                PLUGIN_DIR,
                "..",
                "schema_0_4",
                "schema_information.json",
            )
        ) as fp:
            self._schema_information = json.load(fp)

    def _set_key_in_dict_for_export(
        self, data, key, value, column_info={}, open_codelist_ids_to_codes_mappings={}
    ):
        # ------------ data check
        # Check for isNull on pyQt QVariant
        if value is None or (hasattr(value, "isNull") and value.isNull()):
            return

        # ------------ setup
        key_bits = key.split("/")
        final_key = key_bits.pop(-1)

        # ------------ Work our way down to the dictionary we actually want to set
        for key_bit in key_bits:
            if key_bit in data:
                data = data[key_bit]
            else:
                data[key_bit] = {}
                data = data[key_bit]

        # ------------ now set, taking into account the column type
        column_type = column_info.get("type")
        if column_type == "boolean":
            data[final_key] = value == "true"
        elif column_type == "integer":
            data[final_key] = int(value)
        elif column_type == "number":
            data[final_key] = float(value)
        elif column_type == "foreign_key":
            data[final_key] = self._tables_ids_to_standard_info_mappings[
                column_info["foreignkey_layer"]
            ][value]["id"]
        elif column_type == "foreign_key_id_name_dict":
            info = self._tables_ids_to_standard_info_mappings[
                column_info["foreignkey_layer"]
            ][value]
            data[final_key] = {"id": info["id"], "name": info["name"]}
        elif (
            column_type == "open_codelist"
            and value in open_codelist_ids_to_codes_mappings
        ):
            data[final_key] = open_codelist_ids_to_codes_mappings[value]
        else:
            data[final_key] = value

    def go(self):
        # Make JSON
        networks = {}
        # Load Codelist data we may need later
        open_codelists_ids_to_codes_mappings = {}
        for open_codelist_name in self._schema_information["open_codelists"].keys():
            open_codelists_ids_to_codes_mappings[open_codelist_name] = {}
            for data in self._callable("codelist_open_" + open_codelist_name[:-4]):
                open_codelists_ids_to_codes_mappings[open_codelist_name][data["id"]] = (
                    data["code"]
                )
        # Load table data that is the target of foreign keys for use later
        self._tables_ids_to_standard_info_mappings = {}
        for table_name in ["nodes", "networks", "organisations", "phases"]:
            self._tables_ids_to_standard_info_mappings[table_name] = {}
            for data in self._callable(table_name):
                self._tables_ids_to_standard_info_mappings[table_name][data["id"]] = {
                    "id": data["ofds_id"],
                    "name": data["name"] if "name" in data.keys() else None,
                }
        # Networks first
        for data in self._callable("networks"):
            network_ofds_id = data["ofds_id"]
            # If they put in a network but didn't set an id for it, we'll set one for them
            if not network_ofds_id:
                network_ofds_id = str(uuid.uuid4())
            networks[network_ofds_id] = copy.deepcopy(START_OF_NETWORK)
            networks[network_ofds_id]["id"] = network_ofds_id
            for column_info in self._schema_information["tables"]["networks"][
                "columns"
            ]:
                if column_info["name"] != "ofds_id":
                    self._set_key_in_dict_for_export(
                        networks[network_ofds_id],
                        column_info["name"].replace("__", "/"),
                        data[column_info["name"]],
                        column_info=column_info,
                        open_codelist_ids_to_codes_mappings=(
                            open_codelists_ids_to_codes_mappings[
                                column_info["codelist"]
                            ]
                            if column_info["type"] == "open_codelist"
                            else {}
                        ),
                    )
        # If they didn't set any networks, we'll create one, as we need it!
        if not networks:
            network_ofds_id = str(uuid.uuid4())
            networks[network_ofds_id] = copy.deepcopy(START_OF_NETWORK)
            networks[network_ofds_id]["id"] = network_ofds_id
            self._tables_ids_to_standard_info_mappings["networks"][1] = {
                "id": network_ofds_id
            }
        # Other tables - first load geopackage id's to json id mapping
        geopackage_id_to_standard_info_mappings = {}
        for table_name in [
            "nodes",
            "spans",
            "phases",
            "organisations",
            "contracts",
            "wayleaves",
        ]:
            geopackage_id_to_standard_info_mappings[table_name] = {}
            for data in self._callable(table_name):
                if table_name == "wayleaves":
                    geopackage_id_to_standard_info_mappings[table_name][data["id"]] = (
                        data["ofds_id"]
                    )
                else:
                    geopackage_id_to_standard_info_mappings[table_name][data["id"]] = {
                        "id": data["ofds_id"],
                        "name": data["name"] if "name" in data.keys() else None,
                    }
        # Other tables - now process
        for table_name, sub_tables in [
            ("nodes", [("internationalConnections", "node_id")]),
            ("spans", []),
            ("phases", []),
            ("organisations", []),
            ("contracts", [("documents", "contract_id")]),
            ("wayleaves", []),
        ]:
            for data in self._callable(table_name):
                out = {}
                network_table_id = data["network_id"] or 1
                network_ofds_id = self._tables_ids_to_standard_info_mappings[
                    "networks"
                ][network_table_id]["id"]
                # Normal fields
                out["id"] = data["ofds_id"] or str(uuid.uuid4())
                for column_info in self._schema_information["tables"][table_name][
                    "columns"
                ]:
                    if column_info["name"] not in ["ofds_id", "network_id"]:
                        self._set_key_in_dict_for_export(
                            out,
                            column_info["name"].replace("__", "/"),
                            data[column_info["name"]],
                            column_info=column_info,
                            open_codelist_ids_to_codes_mappings=(
                                open_codelists_ids_to_codes_mappings[
                                    column_info["codelist"]
                                ]
                                if column_info["type"] == "open_codelist"
                                else {}
                            ),
                        )
                if self._schema_information["tables"][table_name]["geographic_field"]:
                    geom_data = data["geom"]
                    if geom_data:
                        geom_data = json.loads(geom_data)
                        if geom_data:
                            out[
                                self._schema_information["tables"][table_name][
                                    "geographic_field"
                                ]
                            ] = geom_data
                # other tables
                # This is an inefficient way of doing this, as we loop within loop - but will do for first pass and the small data sizes we expect
                for sub_table_and_field_name, parent_field_name in sub_tables:
                    sub_values = []
                    for sub_table_data in self._callable(
                        table_name + "_" + sub_table_and_field_name
                    ):
                        if (
                            sub_table_data[parent_field_name] == data["id"]
                            and sub_table_data["network_id"] == network_table_id
                        ):
                            sub_out = {}
                            for column_info in self._schema_information["tables"][
                                table_name + "_" + sub_table_and_field_name
                            ]["columns"]:
                                if column_info["name"] not in [
                                    parent_field_name,
                                    "network_id",
                                ]:
                                    self._set_key_in_dict_for_export(
                                        sub_out,
                                        column_info["name"].replace("__", "/"),
                                        sub_table_data[column_info["name"]],
                                        column_info=column_info,
                                        open_codelist_ids_to_codes_mappings=(
                                            open_codelists_ids_to_codes_mappings[
                                                column_info["codelist"]
                                            ]
                                            if column_info["type"] == "open_codelist"
                                            else {}
                                        ),
                                    )
                            sub_values.append(sub_out)
                    if sub_values:
                        out[sub_table_and_field_name] = sub_values

                # relations
                # This is an inefficient way of doing this, as we loop within loop - but will do for first pass and the small data sizes we expect
                for relation in self._schema_information["tables"][table_name].get(
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
                        for related_data in self._callable(relation["related_table"]):
                            geopackage_id_to_standard_info_mappings[
                                relation["related_table"]
                            ][related_data["id"]] = related_data["code"]

                    # Now process
                    values = []
                    for relation_data in self._callable(relation["mapping_table"]):
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
                networks[network_ofds_id][table_name].append(out)

        # Clear empty arrays out of networks
        for network in networks.values():
            for key in [
                "nodes",
                "spans",
                "phases",
                "organisations",
                "contracts",
                "wayleaves",
            ]:
                if not network[key]:
                    del network[key]
        # Wrap up
        return {"networks": [v for v in networks.values()]}
