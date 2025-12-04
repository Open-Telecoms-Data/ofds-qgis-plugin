import json
import os
import sqlite3
import uuid

from .lib import get_deep_key_from_data_for_import

PLUGIN_DIR = os.path.dirname(__file__)


def import_json_to_sqlite(json_data_to_import, sqlite_filename):
    # Setup
    connection = sqlite3.connect(sqlite_filename)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Start
    def callable_write(table_name, data):
        cursor.execute(
            "INSERT INTO "
            + table_name
            + " ("
            + ",".join([i[0] for i in data])
            + ") VALUES ("
            + ",".join(["?" for i in data])
            + ")",
            [i[1] for i in data],
        )

        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]

    def callable_read(table_name):
        cursor.execute("SELECT * FROM " + table_name)
        return cursor.fetchall()

    import_json_to_callable = ImportJSONToCallable(
        json_data_to_import, callable_write, callable_read
    )
    import_json_to_callable.go()

    # Wrap up
    connection.commit()
    connection.close()


class ImportJSONToCallable:

    def __init__(self, json_data_to_import, callable_write, callable_read):
        self._json_data_to_import = json_data_to_import
        self._callable_write = callable_write
        self._callable_read = callable_read
        # Get Information
        with open(
            os.path.join(
                PLUGIN_DIR,
                "..",
                "schema_0_3",
                "schema_information.json",
            )
        ) as fp:
            self._schema_information = json.load(fp)

    def go(self):
        # For each network ...
        networks = self._json_data_to_import.get("networks", [])
        if isinstance(networks, list):
            for network in networks:
                self._go_network(network)

    def _go_network(self, network):
        # Network table
        network_id = network["id"] or uuid.uuid4()
        data = []
        for column_info in self._schema_information["tables"]["networks"]["columns"]:
            if column_info["name"] == "ofds_id":
                data.append(("ofds_id", network_id))
            else:
                data.append(
                    (
                        column_info["name"],
                        get_deep_key_from_data_for_import(
                            network,
                            column_info["name"].replace("__", "/"),
                            type=column_info["type"],
                        ),
                    )
                )
        self._callable_write("networks", data)
        # Now other tables
        standard_id_to_geopackage_id_mappings = {}
        list_idx_to_geopackage_id_mappings = {}
        list_idx_to_thing_id_mappings = {}
        # First pass, make main tables and store mappings
        for table_name in [
            "nodes",
            "spans",
            "phases",
            "organisations",
            "contracts",
        ]:
            table_datas = network.get(table_name, [])
            standard_id_to_geopackage_id_mappings[table_name] = {}
            list_idx_to_geopackage_id_mappings[table_name] = {}
            list_idx_to_thing_id_mappings[table_name] = {}
            if isinstance(table_datas, list):
                for idx, table_data in enumerate(table_datas):
                    thing_id = table_data.get("id") or uuid.uuid4()
                    list_idx_to_thing_id_mappings[table_name][idx] = thing_id
                    data = [("network_id", network_id), ("ofds_id", thing_id)]
                    for column_info in self._schema_information["tables"][table_name][
                        "columns"
                    ]:
                        if column_info["name"] not in ["ofds_id", "network_id"]:
                            data.append(
                                (
                                    column_info["name"],
                                    get_deep_key_from_data_for_import(
                                        table_data,
                                        column_info["name"].replace("__", "/"),
                                        type=column_info["type"],
                                    ),
                                )
                            )
                    if self._schema_information["tables"][table_name][
                        "geographic_field"
                    ]:
                        geom_data = table_data.get(
                            self._schema_information["tables"][table_name][
                                "geographic_field"
                            ]
                        )
                        if isinstance(geom_data, dict):
                            data.append(("geom", json.dumps(geom_data)))
                        else:
                            data.append(("geom", ""))
                    geopackage_id = self._callable_write(table_name, data)
                    standard_id_to_geopackage_id_mappings[table_name][
                        thing_id
                    ] = geopackage_id
                    list_idx_to_geopackage_id_mappings[table_name][idx] = geopackage_id
        # Second pass, some tables underneath the main tables
        for table_name, sub_table_and_field_name, parent_field_name in [
            ("nodes", "internationalConnections", "node_id"),
            ("contracts", "documents", "contract_id"),
        ]:
            table_datas = network.get(table_name, [])
            if isinstance(table_datas, list):
                for idx, table_data in enumerate(table_datas):
                    sub_table_datas = table_data.get(sub_table_and_field_name)
                    if isinstance(sub_table_datas, list):
                        for sub_table_data in sub_table_datas:
                            data = [
                                ("network_id", network_id),
                                (
                                    parent_field_name,
                                    list_idx_to_thing_id_mappings[table_name][idx],
                                ),
                            ]
                            for column_info in self._schema_information["tables"][
                                table_name + "_" + sub_table_and_field_name
                            ]["columns"]:
                                if column_info["name"] not in [
                                    parent_field_name,
                                    "network_id",
                                ]:
                                    data.append(
                                        (
                                            column_info["name"],
                                            get_deep_key_from_data_for_import(
                                                sub_table_data,
                                                column_info["name"].replace("__", "/"),
                                                type=column_info["type"],
                                            ),
                                        )
                                    )
                            self._callable_write(
                                table_name + "_" + sub_table_and_field_name,
                                data,
                            )
        # Third pass, relations
        for table_name in [
            "nodes",
            "spans",
            "phases",
            "organisations",
            "contracts",
        ]:
            table_datas = network.get(table_name, [])
            if isinstance(table_datas, list):
                for relation in self._schema_information["tables"][table_name].get(
                    "relations", []
                ):
                    # First, for codelist, we may have to load the codelist contents to memory
                    if (
                        relation.get("codelist")
                        and relation["related_table"]
                        not in standard_id_to_geopackage_id_mappings
                    ):
                        standard_id_to_geopackage_id_mappings[
                            relation["related_table"]
                        ] = {}
                        for related_data in self._callable_read(
                            relation["related_table"]
                        ):
                            standard_id_to_geopackage_id_mappings[
                                relation["related_table"]
                            ][related_data["code"]] = related_data["id"]

                    # Now process
                    for idx, table_data in enumerate(table_datas):
                        relation_datas = table_data.get(relation["standard_field"])
                        if isinstance(relation_datas, list):
                            for relation_data in relation_datas:
                                relation_data_id = (
                                    relation_data
                                    if relation.get("codelist")
                                    else relation_data.get("id")
                                )
                                if relation_data_id:
                                    self._callable_write(
                                        relation["mapping_table"],
                                        [
                                            (
                                                "base_id",
                                                list_idx_to_geopackage_id_mappings[
                                                    table_name
                                                ][idx],
                                            ),
                                            (
                                                "related_id",
                                                standard_id_to_geopackage_id_mappings[
                                                    relation["related_table"]
                                                ][relation_data_id],
                                            ),
                                        ],
                                    )
