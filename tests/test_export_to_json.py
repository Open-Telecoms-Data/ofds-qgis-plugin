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
    cursor.execute(
        "INSERT INTO networks (ofds_id, name, publisher__name, accuracy) VALUES ('netty', 'Network', 'Publisher', 1.2)"
    )
    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["id"] == "netty"
    assert data["networks"][0]["name"] == "Network"
    assert data["networks"][0]["publisher"]["name"] == "Publisher"
    assert data["networks"][0]["accuracy"] == 1.2
    # there are no contracts here, and empty arrays should be removed
    assert "contracts" not in data["networks"][0].keys()


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


def test_export_network_with_id_and_organisation_and_node_and_org_and_node_linked():
    """Tests a network with an org and a node. The org is in the node's networkProviders."""
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO networks (ofds_id, name) VALUES ('netty', 'Network')")
    # TODO Hard coding the id's is a bit of an assumption but we are getting away with it
    cursor.execute(
        "INSERT INTO organisations (ofds_id, name, network_id) VALUES ('orga', 'Org A', 1)"
    )
    cursor.execute(
        "INSERT INTO nodes (ofds_id, name, network_id, geom) VALUES ('nodea', 'Node A', 1, '{}')"
    )
    cursor.execute(
        "INSERT INTO relation_nodes_networkProviders(base_id, related_id) VALUES (1, 1)"
    )
    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["id"] == "netty"
    assert data["networks"][0]["name"] == "Network"
    assert data["networks"][0]["organisations"][0] == {"id": "orga", "name": "Org A"}
    assert data["networks"][0]["nodes"][0]["id"] == "nodea"
    assert data["networks"][0]["nodes"][0]["name"] == "Node A"
    assert data["networks"][0]["nodes"][0]["networkProviders"][0]["id"] == "orga"


def test_export_contract_documents_1():
    """
    Export some contract documents

    It has contracts of the same ID in different networks, which is alowed in the spec!

    """
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO networks (ofds_id, name) VALUES ('netty', 'Network'),('worky', 'Network')"
    )
    # TODO Hard coding the id's is a bit of an assumption but we are getting away with it
    cursor.execute(
        """
        INSERT INTO contracts (ofds_id, title, network_id) 
        VALUES ('contracta', 'Contract A', 1),('contractb', 'Contract B', 1), 
        ('contracta', 'Contract A', 2),('contractb', 'Contract B', 2)
        """
    )
    cursor.execute(
        """
        INSERT INTO contracts_documents (title, network_id, contract_id) 
        VALUES ('documenta', 1, 1),('documentb', 1, 2),
        ('documentc', 2, 3),('documentd', 2, 4)
        """
    )

    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["contracts"] == [
        {
            "id": "contracta",
            "title": "Contract A",
            "documents": [{"title": "documenta"}],
        },
        {
            "id": "contractb",
            "title": "Contract B",
            "documents": [{"title": "documentb"}],
        },
    ]
    assert data["networks"][1]["contracts"] == [
        {
            "id": "contracta",
            "title": "Contract A",
            "documents": [{"title": "documentc"}],
        },
        {
            "id": "contractb",
            "title": "Contract B",
            "documents": [{"title": "documentd"}],
        },
    ]


def test_export_mulitple_codelists_1():
    """
    Export some contract documents

    It has contracts of the same ID in different networks, which is alowed in the spec!

    """
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO networks (ofds_id, name) VALUES ('netty', 'Network'),('worky', 'Network')"
    )
    # TODO Hard coding the id's is a bit of an assumption but we are getting away with it
    cursor.execute(
        "INSERT INTO nodes (ofds_id, name, network_id, geom) VALUES ('nodea', 'Node A', 1, '{}')"
    )
    cursor.execute("INSERT INTO relation_nodes_type(base_id, related_id) VALUES (1, 1)")

    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["nodes"][0]["type"] == ["addDropSite"]


def test_export_custom_single_open_codelist_entry_1():
    """
    For a open codelist field (single value), add a custom codelist item then set it and export it.
    """
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO networks (ofds_id, name) VALUES ('netty', 'Network'),('worky', 'Network')"
    )
    cursor.execute(
        "INSERT INTO codelist_open_organisationIdentifierScheme (code, description) VALUES ('MYOWNORGLIST','Using org-id is too hard so I just made up my own prefix')"
    )
    cursor.execute("SELECT last_insert_rowid()")
    new_codelist_item_id = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO organisations (ofds_id, name, network_id, identifier__scheme) VALUES ('orga', 'Org A', 1, ?)",
        [new_codelist_item_id],
    )
    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["organisations"][0] == {
        "id": "orga",
        "identifier": {
            "scheme": "MYOWNORGLIST",
        },
        "name": "Org A",
    }


def test_span_with_start_and_end_set_1():
    sqlite_filename = _get_and_setup_sqlite_filename()

    # Set Some data
    connection = sqlite3.connect(sqlite_filename)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO networks (ofds_id, name) VALUES ('netty', 'Network')")
    cursor.execute(
        "INSERT INTO nodes (network_id, ofds_id, geom) VALUES (1, 'node1', '{}'), (1, 'node2','{}')"
    )
    cursor.execute(
        "INSERT INTO spans (ofds_id, network_id, start, end, geom) VALUES ('span1to2', 1, 1, 2, '{}')",
    )
    connection.commit()
    connection.close()

    # Export
    data = export_sqlite_to_json(sqlite_filename)

    # Test
    assert data["networks"][0]["spans"][0] == {
        "id": "span1to2",
        "start": "node1",
        "end": "node2",
        "route": {},
    }
