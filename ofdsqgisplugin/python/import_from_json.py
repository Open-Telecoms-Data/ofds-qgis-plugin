import json
import os
import sqlite3
import uuid

from .lib import get_deep_key_from_data_for_import

PLUGIN_DIR = os.path.dirname(__file__)


def import_json_to_sqlite(json_data_to_import, sqlite_filename):
    # Setup
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()

    # Start
    def callable(table_name, data):
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

    import_json_to_callable(json_data_to_import, callable)
    # Wrap up
    connection.commit()
    connection.close()


def import_json_to_callable(json_data_to_import, callable):
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
    # Start at networks
    networks = json_data_to_import.get("networks", [])
    if isinstance(networks, list):
        for network in networks:
            network_id = network["id"] or uuid.uuid4()
            data = []
            for column_info in schema_information["tables"]["networks"]["columns"]:
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
            callable("networks", data)
            # Now other tables
            standard_id_to_geopackage_id_mappings = {}
            list_idx_to_geopackage_id_mappings = {}
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
                if isinstance(table_datas, list):
                    for idx, table_data in enumerate(table_datas):
                        thing_id = table_data.get("id") or uuid.uuid4()
                        data = [("network_id", network_id), ("ofds_id", thing_id)]
                        for column_info in schema_information["tables"][table_name][
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
                        if schema_information["tables"][table_name]["geographic_field"]:
                            geom_data = table_data.get(
                                schema_information["tables"][table_name][
                                    "geographic_field"
                                ]
                            )
                            if isinstance(geom_data, dict):
                                data.append(("geom", json.dumps(geom_data)))
                            else:
                                data.append(("geom", ""))
                        geopackage_id = callable(table_name, data)
                        standard_id_to_geopackage_id_mappings[table_name][
                            thing_id
                        ] = geopackage_id
                        list_idx_to_geopackage_id_mappings[table_name][
                            idx
                        ] = geopackage_id
            # Second pass, relations
            for table_name in [
                "nodes",
                "spans",
                "phases",
                "organisations",
                "contracts",
            ]:
                table_datas = network.get(table_name, [])
                if isinstance(table_datas, list):
                    for relation in schema_information["tables"][table_name].get(
                        "relations", []
                    ):
                        for idx, table_data in enumerate(table_datas):
                            relation_datas = table_data.get(relation["standard_field"])
                            if isinstance(relation_datas, list):
                                for relation_data in relation_datas:
                                    relation_data_id = relation_data.get("id")
                                    if relation_data_id:
                                        callable(
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
                                                    ][
                                                        relation_data_id
                                                    ],
                                                ),
                                            ],
                                        )
