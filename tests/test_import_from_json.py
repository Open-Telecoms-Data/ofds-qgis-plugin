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
                    "name": "Network 1",
                    "organisations": [{"id": "orga", "name": "Org A"}],
                    "publisher": { "name": "Publisher"},
                    "accuracy": 2.3
                },
                {
                    "id": "network2",
                    "name": "Network 2",
                    "organisations": [{"id": "orgb", "name": "Org B"}],
                },
            ]
        },
        sqlite_filename,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    # networks
    cursor.execute("SELECT ofds_id, name, publisher__name, accuracy FROM networks ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert ("network1", "Network 1", "Publisher", 2.3) == rows[0]
    assert ("network2", "Network 2", None, None) == rows[1]
    # organisations
    cursor.execute(
        "SELECT ofds_id, name, network_id FROM organisations ORDER BY ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert ("orga", "Org A", "network1") == rows[0]
    assert ("orgb", "Org B", "network2") == rows[1]
    connection.close()
