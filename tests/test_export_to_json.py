import os
import shutil
import sqlite3
import tempfile

from ofdsqgisplugin.python.export_to_json import export_sqlite_to_json

PLUGIN_DIR = os.path.dirname(__file__)


def _get_and_setup_sqlite_filename():
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
    # Out
    return sqlite_filename


def test_export_network_with_id():
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO networks (ofds_id, name, publisher__name) VALUES ('netty', 'Network', 'Publisher')")
    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["id"] == "netty"
    assert data["networks"][0]["name"] == "Network"
    assert data["networks"][0]["publisher"]["name"] == "Publisher"


def test_export_network_with_no_id():
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO networks (name) VALUES ('Network')")
    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test that the export code set an UUID as the Id for us
    assert len(data["networks"][0]["id"]) == 36
    assert data["networks"][0]["name"] == "Network"


def test_export_network_with_id_and_organisation():
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO networks (ofds_id, name) VALUES ('netty', 'Network')")
    cursor.execute(
        "INSERT INTO organisations (ofds_id, name, network_id) VALUES ('orga', 'Org A', 'netty')"
    )
    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["id"] == "netty"
    assert data["networks"][0]["name"] == "Network"
    assert data["networks"][0]["organisations"][0] == {"id": "orga", "name": "Org A"}
