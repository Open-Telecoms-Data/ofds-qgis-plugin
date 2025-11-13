import json
import os
import shutil
import sqlite3

MAP_FIELD_TYPES_TO_SQLITE_TYPES = {"boolean": "int", "integer": "int", "number": "real"}


class Builder:

    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.connection = None
        self.cursor = None
        self.information_out = None

    def create_table_from_json_schema(
        self,
        json_schema,
        table_name,
        has_network_id=False,
        geographic_type=None,
        geographic_field=None,
    ):
        columns = []
        for property_key, property_value in json_schema["properties"].items():
            if property_value["type"] == "string":
                columns.append(
                    {
                        "name": ("ofds_id" if property_key == "id" else property_key),
                        "type": "text",
                    }
                )

        if has_network_id:
            columns.append({"name": "network_id", "type": "text"})

        fields_sql = [i["name"] + " " + i["type"] for i in columns]
        self.cursor.execute(
            """
            CREATE TABLE {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {}
                {}
            );
        """.format(
                table_name,
                "geom BLOB NOT NULL," if geographic_type else "",
                ",".join(fields_sql),
            )
        )

        self.cursor.execute(
            """
            INSERT INTO gpkg_contents (table_name, data_type, identifier, srs_id)
            VALUES ('{}', '{}', '{}', 4326);
        """.format(
                table_name,
                "features" if geographic_type else "attributes",
                table_name,
            )
        )

        if geographic_type:
            self.cursor.execute(
                """
                INSERT INTO gpkg_geometry_columns (
                    table_name, column_name, geometry_type_name, srs_id, z, m
                ) VALUES ('{}', 'geom', '{}', 4326, 0, 0);
            """.format(
                    table_name, geographic_type
                )
            )

        self.information_out["tables"][table_name] = {
            "columns": columns,
            "geographic_type": geographic_type,
            "geographic_field": geographic_field,
        }

    def go(self):
        # Load JSON Schema
        jsonschema_filename = os.path.join(
            self.root_directory,
            "buildofdsqgisplugin",
            "schema_0_3",
            "schema.json",
        )
        with open(jsonschema_filename) as fp:
            jsonschema = json.load(fp)
        # Copy GeoPackage
        sqlite_filename = os.path.join(
            self.root_directory,
            "ofdsqgisplugin",
            "schema_0_3",
            "geopackage.gpkg",
        )
        shutil.copyfile(
            os.path.join(
                self.root_directory,
                "buildofdsqgisplugin",
                "empty.gpkg",
            ),
            sqlite_filename,
        )
        # Setup
        self.connection = sqlite3.connect(sqlite_filename)
        self.cursor = self.connection.cursor()
        self.information_out = {"tables": {}}
        # Create Tables
        self.create_table_from_json_schema(jsonschema, table_name="networks")
        self.create_table_from_json_schema(
            jsonschema["properties"]["nodes"]["items"],
            table_name="nodes",
            has_network_id=True,
            geographic_field="location",
            geographic_type="POINT",
        )
        self.create_table_from_json_schema(
            jsonschema["properties"]["spans"]["items"],
            table_name="spans",
            has_network_id=True,
            geographic_field="route",
            geographic_type="LINESTRING",
        )
        self.create_table_from_json_schema(
            jsonschema["properties"]["phases"]["items"],
            table_name="phases",
            has_network_id=True,
        )
        self.create_table_from_json_schema(
            jsonschema["properties"]["organisations"]["items"],
            table_name="organisations",
            has_network_id=True,
        )
        self.create_table_from_json_schema(
            jsonschema["properties"]["contracts"]["items"],
            table_name="contracts",
            has_network_id=True,
        )
        # Wrapup
        self.connection.commit()
        schema_information_json_filename = os.path.join(
            self.root_directory,
            "ofdsqgisplugin",
            "schema_0_3",
            "schema_information.json",
        )
        with open(schema_information_json_filename, "w") as fp:
            json.dump(self.information_out, fp, indent=2)


if __name__ == "__main__":
    builder = Builder(
        root_directory=os.path.realpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
        ),
    )
    builder.go()
