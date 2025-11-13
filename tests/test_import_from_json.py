import os
import shutil
import sqlite3
import tempfile

from ofdsqgisplugin.python.import_from_json import import_json_to_sqlite

PLUGIN_DIR = os.path.dirname(__file__)


def test_import_1():
    # Get new SQLite filename
    sqlite_filename = tempfile.mkstemp(suffix=".sqlite")
    os.close(sqlite_filename[0])
    sqlite_filename = sqlite_filename[1]
    # Copy template
    shutil.copyfile(
        os.path.join(
            PLUGIN_DIR,
            "..",
            "ofdsqgisplugin",
            "schema_0_3",
            "geopackage.gpkg",
        ),
        sqlite_filename,
    )

    # Do the import
    import_json_to_sqlite(
        {
            "networks": [
                {
                    "id": "network1",
                    "name": "name",
                }
            ]
        },
        sqlite_filename,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute("SELECT ofds_id, name FROM networks ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert ("network1", "name") == rows[0]
    connection.close()
