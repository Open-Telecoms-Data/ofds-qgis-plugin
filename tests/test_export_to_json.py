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
    cursor.execute(
        "INSERT INTO organisations (ofds_id, name, network_id) VALUES ('orga', 'Org A', 'netty')"
    )
    cursor.execute(
        "INSERT INTO nodes (ofds_id, name, network_id, geom) VALUES ('nodea', 'Node A', 'netty', '{}')"
    )
    # TODO Hard coding the id's is a bit of an assumption but we are getting away with it
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
    cursor.execute(
        """
        INSERT INTO contracts (ofds_id, title, network_id) 
        VALUES ('contracta', 'Contract A', 'netty'),('contractb', 'Contract B', 'netty'), 
        ('contracta', 'Contract A', 'worky'),('contractb', 'Contract B', 'worky')
        """
    )
    cursor.execute(
        """
        INSERT INTO contracts_documents (title, network_id, contract_id) 
        VALUES ('documenta', 'netty', 'contracta'),('documentb', 'netty', 'contractb'),
        ('documentc', 'worky', 'contracta'),('documentd', 'worky', 'contractb')
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
