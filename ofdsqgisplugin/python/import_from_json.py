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
    # Start
    networks = json_data_to_import.get("networks", [])
    if isinstance(networks, list):
        for network in networks:
            data = []
            for column_info in schema_information["tables"]["networks"]["columns"]:
                if column_info["name"] == "ofds_id":
                    data.append(("ofds_id", network["id"] or uuid.uuid4()))
                else:
                    data.append(
                        (
                            column_info["name"],
                            get_deep_key_from_data_for_import(
                                network, column_info["name"]
                            ),
                        )
                    )
            callable("networks", data)
