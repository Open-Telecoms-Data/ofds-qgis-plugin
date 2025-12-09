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
                    "publisher": {"name": "Publisher"},
                    "accuracy": 2.3,
                    "nodes": [
                        {
                            "id": "node1",
                            "physicalInfrastructureProvider": {"id": "orga"},
                        }
                    ],
                },
                {
                    "id": "network2",
                    "name": "Network 2",
                    "organisations": [{"id": "orgb", "name": "Org B"}],
                },
            ]
        },
        sqlite_filename,
        enforce_foreign_keys=True,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    # networks
    cursor.execute(
        "SELECT id, ofds_id, name, publisher__name, accuracy FROM networks ORDER BY ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert (1, "network1", "Network 1", "Publisher", 2.3) == rows[0]
    assert (2, "network2", "Network 2", None, None) == rows[1]
    # organisations
    cursor.execute(
        "SELECT ofds_id, name, network_id FROM organisations ORDER BY ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert ("orga", "Org A", 1) == rows[0]
    assert ("orgb", "Org B", 2) == rows[1]
    # nodes
    cursor.execute(
        "SELECT ofds_id, physicalInfrastructureProvider, network_id FROM nodes ORDER BY ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert ("node1", 1, 1) == rows[0]
    # wrapup
    connection.close()


def test_import_nodes_network_providers_1():
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
                    "organisations": [
                        {"id": "orga", "name": "Org A"},
                        {"id": "orgb", "name": "Org B"},
                    ],
                    "nodes": [
                        {"id": "node1", "networkProviders": [{"id": "orga"}]},
                        {"id": "node2", "networkProviders": [{"id": "orgb"}]},
                    ],
                },
            ]
        },
        sqlite_filename,
        enforce_foreign_keys=True,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    # networks
    cursor.execute("SELECT id, ofds_id, name FROM networks ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert (1, "network1", "Network 1") == rows[0]
    # organisations
    cursor.execute(
        "SELECT ofds_id, name, network_id FROM organisations ORDER BY ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert ("orga", "Org A", 1) == rows[0]
    assert ("orgb", "Org B", 1) == rows[1]
    # nodes
    cursor.execute("SELECT ofds_id, network_id FROM nodes ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert ("node1", 1) == rows[0]
    assert ("node2", 1) == rows[1]
    # nodes network providers
    cursor.execute(
        """
        SELECT nodes.ofds_id, organisations.ofds_id
        FROM relation_nodes_networkProviders
        JOIN nodes ON nodes.id == relation_nodes_networkProviders.base_id
        JOIN organisations ON organisations.id = relation_nodes_networkProviders.related_id
        ORDER BY nodes.ofds_id ASC
        """
    )
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert ("node1", "orga") == rows[0]
    assert ("node2", "orgb") == rows[1]
    # wrapup
    connection.close()


def test_import_contract_documents_1():
    """
    Import some contract documents

    It has contracts of the same ID in different networks, which is alowed in the spec!
    """
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
                    "contracts": [
                        {
                            "id": "contracta",
                            "title": "titlea",
                            "documents": [{"title": "A-1"}, {"title": "A-2"}],
                        },
                        {
                            "id": "contractb",
                            "title": "titleb",
                            "documents": [{"title": "B-1"}, {"title": "B-2"}],
                        },
                    ],
                },
                {
                    "id": "network2",
                    "name": "Network 2",
                    "contracts": [
                        {
                            "id": "contracta",
                            "title": "titlea",
                            "documents": [{"title": "C-1"}, {"title": "C-2"}],
                        },
                    ],
                },
            ]
        },
        sqlite_filename,
        enforce_foreign_keys=True,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    # networks
    cursor.execute("SELECT id, ofds_id, name FROM networks ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert (1, "network1", "Network 1") == rows[0]
    assert (2, "network2", "Network 2") == rows[1]
    # contracts
    cursor.execute(
        "SELECT network_id, ofds_id, title FROM contracts ORDER BY network_id ASC, ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 3 == len(rows)
    assert (
        1,
        "contracta",
        "titlea",
    ) == rows[0]
    assert (
        1,
        "contractb",
        "titleb",
    ) == rows[1]
    assert (
        2,
        "contracta",
        "titlea",
    ) == rows[2]
    # contract documents
    cursor.execute(
        "SELECT network_id, contract_id, title FROM contracts_documents ORDER BY title ASC"
    )
    rows = cursor.fetchall()
    assert 6 == len(rows)
    assert (1, 1, "A-1") == rows[0]
    assert (1, 1, "A-2") == rows[1]
    assert (1, 2, "B-1") == rows[2]
    assert (1, 2, "B-2") == rows[3]
    assert (2, 3, "C-1") == rows[4]
    assert (2, 3, "C-2") == rows[5]
    # wrapup
    connection.close()


def test_import_multiple_codelists_1():
    """ """
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
                    "nodes": [
                        {"id": "node1", "type": ["addDropSite"]},
                    ],
                },
            ]
        },
        sqlite_filename,
        enforce_foreign_keys=True,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    # networks
    cursor.execute("SELECT id, ofds_id, name FROM networks ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert (1, "network1", "Network 1") == rows[0]
    # nodes
    cursor.execute("SELECT ofds_id, network_id FROM nodes ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert ("node1", 1) == rows[0]
    # node technologies
    cursor.execute(
        """
        SELECT nodes.ofds_id, codelist_open_nodeType.code
        FROM relation_nodes_type
        JOIN nodes ON nodes.id == relation_nodes_type.base_id
        JOIN codelist_open_nodeType ON codelist_open_nodeType.id = relation_nodes_type.related_id
        ORDER BY nodes.ofds_id ASC
        """
    )
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert ("node1", "addDropSite") == rows[0]
    # wrapup
    connection.close()


def test_import_custom_single_open_codelist_entry_1():
    """
    For a open codelist field (single value), import data with a custom codelist item.
    """
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
                    "organisations": [
                        {
                            "id": "orga",
                            "identifier": {
                                "scheme": "MYOWNORGLIST",
                            },
                            "name": "Org A",
                        }
                    ],
                },
            ]
        },
        sqlite_filename,
        enforce_foreign_keys=True,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    # networks
    cursor.execute("SELECT id, ofds_id, name FROM networks ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert (1, "network1", "Network 1") == rows[0]
    # get our new custom item from the open codelist
    cursor.execute(
        "SELECT id, code, description FROM codelist_open_organisationIdentifierScheme WHERE code=?",
        ["MYOWNORGLIST"],
    )
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert "MYOWNORGLIST" == rows[0][1]
    assert "MYOWNORGLIST" == rows[0][2]
    new_codelist_item_id = rows[0][0]
    # organisations
    cursor.execute(
        "SELECT ofds_id, name, network_id, identifier__scheme FROM organisations ORDER BY ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert ("orga", "Org A", 1, new_codelist_item_id) == rows[0]
    # wrapup
    connection.close()


def test_span_with_start_and_end_set_1():
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
                    "nodes": [
                        {
                            "id": "node1",
                        },
                        {
                            "id": "node2",
                        },
                    ],
                    "spans": [{"id": "span1to2", "start": "node1", "end": "node2"}],
                }
            ]
        },
        sqlite_filename,
        enforce_foreign_keys=True,
    )

    # Test the database contents
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    # networks
    cursor.execute("SELECT id, ofds_id, name FROM networks ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert (1, "network1", "Network 1") == rows[0]
    # nodes
    cursor.execute("SELECT id, ofds_id, network_id FROM nodes ORDER BY ofds_id ASC")
    rows = cursor.fetchall()
    assert 2 == len(rows)
    assert (1, "node1", 1) == rows[0]
    assert (2, "node2", 1) == rows[1]
    # spans
    cursor.execute(
        "SELECT id, ofds_id, start, end, network_id FROM spans ORDER BY ofds_id ASC"
    )
    rows = cursor.fetchall()
    assert 1 == len(rows)
    assert (1, "span1to2", 1, 2, 1) == rows[0]
    # wrapup
    connection.close()
