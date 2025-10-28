import json


def get_json(layers):
    # Make JSON
    networks = {}
    network_id = None
    # networks
    for f in layers["networks"].getFeatures():
        network_id = f.attribute("id")
        # If they put in a network but didn't set an id for it, we'll set one for them
        if not network_id:
            network_id = "network"
        networks[network_id] = {
            "id": network_id,
            "name": f.attribute("name") or "",
            # TODO add more fields here
            "nodes": [],
            "spans": [],
        }
    if not network_id:
        network_id = "network"
        networks[network_id] = {
            "id": network_id,
            "name": "Network",
            "nodes": [],
            "spans": [],
        }
    # nodes
    for f in layers["nodes"].getFeatures():
        networks[network_id]["nodes"].append(
            {
                "id": f.attribute("nodes/0/id"),
                "name": f.attribute("nodes/0/name") or "",
                "location": json.loads(f.geometry().asJson()),
            }
        )
    # spans
    for f in layers["spans"].getFeatures():
        networks[network_id]["spans"].append(
            {
                "id": f.attribute("spans/0/id"),
                "name": f.attribute("spans/0/name") or "",
                "route": json.loads(f.geometry().asJson()),
            }
        )
    # done
    return {"networks": [v for v in networks.values()]}
