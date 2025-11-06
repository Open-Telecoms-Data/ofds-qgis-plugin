import json
import os
import shutil
import sqlite3

MAP_FIELD_TYPES_TO_SQLITE_TYPES = {"boolean": "int", "integer": "int", "number": "real"}


def go(root_directory, version_major, version_minor):
    with open(
        os.path.join(
            root_directory,
            "ofdsqgisplugin",
            "schema_{}_{}".format(version_major, version_minor),
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)
    sqlite_filename = os.path.join(
        root_directory,
        "ofdsqgisplugin",
        "schema_{}_{}".format(version_major, version_minor),
        "geopackage.gpkg",
    )
    shutil.copyfile(
        os.path.join(
            root_directory,
            "buildofdsqgisplugin",
            "empty.gpkg",
        ),
        sqlite_filename,
    )
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    for table_name, table_info in schema_information.items():
        fields_sql = []
        for field_information in table_info["fields"]:
            fields_sql.append(
                '"{}" {}'.format(
                    field_information["name"],
                    MAP_FIELD_TYPES_TO_SQLITE_TYPES.get(
                        field_information["type"], "text"
                    ),
                )
            )
        cursor.execute(
            """
            CREATE TABLE {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {}
                {}
            );
        """.format(
                table_name,
                "geom BLOB NOT NULL," if table_info["geometry_type"] else "",
                ",".join(fields_sql),
            )
        )

        cursor.execute(
            """
            INSERT INTO gpkg_contents (table_name, data_type, identifier, srs_id)
            VALUES ('{}', '{}', '{}', 4326);
        """.format(
                table_name,
                "features" if table_info["geometry_type"] else "attributes",
                table_name,
            )
        )

        if table_info["geometry_type"]:
            cursor.execute(
                """
                INSERT INTO gpkg_geometry_columns (
                    table_name, column_name, geometry_type_name, srs_id, z, m
                ) VALUES ('{}', 'geom', '{}', 4326, 0, 0);
            """.format(
                    table_name, table_info["geometry_type"]
                )
            )

    connection.commit()


if __name__ == "__main__":
    go(
        root_directory=os.path.realpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
        ),
        version_major=os.getenv("VERSION_MAJOR"),
        version_minor=os.getenv("VERSION_MINOR"),
    )
