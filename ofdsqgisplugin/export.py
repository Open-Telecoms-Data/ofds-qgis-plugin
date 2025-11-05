import json

from .lib import set_key_in_dict_for_export


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
            "nodes": [],
            "spans": [],
        }
        set_key_in_dict_for_export(networks[network_id], "name", f.attribute("name"))
        set_key_in_dict_for_export(
            networks[network_id], "publisher/id", f.attribute("publisher/id")
        )
        set_key_in_dict_for_export(
            networks[network_id], "publisher/name", f.attribute("publisher/name")
        )
        set_key_in_dict_for_export(
            networks[network_id],
            "publisher/identifier/id",
            f.attribute("publisher/identifier/id"),
        )
        set_key_in_dict_for_export(
            networks[network_id],
            "publisher/identifier/scheme",
            f.attribute("publisher/identifier/scheme"),
        )
        set_key_in_dict_for_export(
            networks[network_id],
            "publisher/identifier/legalName",
            f.attribute("publisher/identifier/legalName"),
        )
        set_key_in_dict_for_export(
            networks[network_id],
            "publisher/identifier/uri",
            f.attribute("publisher/identifier/uri"),
        )
        set_key_in_dict_for_export(
            networks[network_id], "publisher/country", f.attribute("publisher/country")
        )
        set_key_in_dict_for_export(
            networks[network_id], "publisher/roles", f.attribute("publisher/roles")
        )  # TODO this is meant to be a list
        set_key_in_dict_for_export(
            networks[network_id],
            "publisher/roleDetails",
            f.attribute("publisher/roleDetails"),
        )
        set_key_in_dict_for_export(
            networks[network_id], "publisher/website", f.attribute("publisher/website")
        )
        set_key_in_dict_for_export(
            networks[network_id], "publisher/logo", f.attribute("publisher/logo")
        )
        set_key_in_dict_for_export(
            networks[network_id], "publicationDate", f.attribute("publicationDate")
        )
        set_key_in_dict_for_export(
            networks[network_id], "collectionDate", f.attribute("collectionDate")
        )
        set_key_in_dict_for_export(
            networks[network_id], "accuracy", f.attribute("accuracy")
        )
        set_key_in_dict_for_export(
            networks[network_id], "accuracyDetails", f.attribute("accuracyDetails")
        )
        set_key_in_dict_for_export(
            networks[network_id], "language", f.attribute("language")
        )
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
        node_data = {
            "id": f.attribute("nodes/0/id"),
            "location": json.loads(f.geometry().asJson()),
        }
        set_key_in_dict_for_export(node_data, "name", f.attribute("nodes/0/name"))
        set_key_in_dict_for_export(
            node_data, "phase/id", f.attribute("nodes/0/phase/id")
        )
        set_key_in_dict_for_export(node_data, "status", f.attribute("nodes/0/status"))
        set_key_in_dict_for_export(
            node_data,
            "address/streetAddress",
            f.attribute("nodes/0/address/streetAddress"),
        )
        set_key_in_dict_for_export(
            node_data,
            "address/locality",
            f.attribute("nodes/0/address/locality"),
        )
        set_key_in_dict_for_export(
            node_data, "address/region", f.attribute("nodes/0/address/region")
        )
        set_key_in_dict_for_export(
            node_data,
            "address/postalCode",
            f.attribute("nodes/0/address/postalCode"),
        )
        set_key_in_dict_for_export(
            node_data, "address/country", f.attribute("nodes/0/address/country")
        )
        set_key_in_dict_for_export(node_data, "type", f.attribute("nodes/0/type"))
        set_key_in_dict_for_export(
            node_data, "accessPoint", f.attribute("nodes/0/accessPoint")
        )
        set_key_in_dict_for_export(node_data, "power", f.attribute("nodes/0/power"))
        set_key_in_dict_for_export(
            node_data, "technologies", f.attribute("nodes/0/technologies")
        )
        set_key_in_dict_for_export(
            node_data,
            "physicalInfrastructureProvider/id",
            f.attribute("nodes/0/physicalInfrastructureProvider/id"),
        )
        set_key_in_dict_for_export(
            node_data,
            "networkProviders/0/id",
            f.attribute("nodes/0/networkProviders/0/id"),
        )
        networks[network_id]["nodes"].append(node_data)
    # spans
    for f in layers["spans"].getFeatures():
        span_data = {
            "id": f.attribute("spans/0/id"),
            "route": json.loads(f.geometry().asJson()),
        }
        set_key_in_dict_for_export(span_data, "name", f.attribute("spans/0/name"))
        set_key_in_dict_for_export(
            span_data, "phase/id", f.attribute("spans/0/phase/id")
        )
        set_key_in_dict_for_export(span_data, "status", f.attribute("spans/0/status"))
        set_key_in_dict_for_export(
            span_data,
            "readyForServiceDate",
            f.attribute("spans/0/readyForServiceDate"),
        )
        set_key_in_dict_for_export(span_data, "start", f.attribute("spans/0/start"))
        set_key_in_dict_for_export(span_data, "end", f.attribute("spans/0/end"))
        set_key_in_dict_for_export(
            span_data, "directed", f.attribute("spans/0/directed")
        )
        set_key_in_dict_for_export(
            span_data,
            "physicalInfrastructureProvider/id",
            f.attribute("spans/0/physicalInfrastructureProvider/id"),
        )
        set_key_in_dict_for_export(
            span_data, "supplier/id", f.attribute("spans/0/supplier/id")
        )
        set_key_in_dict_for_export(
            span_data,
            "transmissionMedium",
            f.attribute("spans/0/transmissionMedium"),
        )
        set_key_in_dict_for_export(
            span_data, "deployment", f.attribute("spans/0/deployment")
        )
        set_key_in_dict_for_export(
            span_data,
            "deploymentDetails/description",
            f.attribute("spans/0/deploymentDetails/description"),
        )
        set_key_in_dict_for_export(
            span_data, "darkFibre", f.attribute("spans/0/darkFibre")
        )
        set_key_in_dict_for_export(
            span_data, "fibreType", f.attribute("spans/0/fibreType")
        )
        set_key_in_dict_for_export(
            span_data,
            "fibreTypeDetails/fibreSubtype",
            f.attribute("spans/0/fibreTypeDetails/fibreSubtype"),
        )
        set_key_in_dict_for_export(
            span_data,
            "fibreTypeDetails/description",
            f.attribute("spans/0/fibreTypeDetails/description"),
        )
        set_key_in_dict_for_export(
            span_data, "fibreCount", f.attribute("spans/0/fibreCount")
        )
        set_key_in_dict_for_export(
            span_data, "fibreLength", f.attribute("spans/0/fibreLength")
        )
        set_key_in_dict_for_export(
            span_data, "technologies", f.attribute("spans/0/technologies")
        )
        set_key_in_dict_for_export(
            span_data, "capacity", f.attribute("spans/0/capacity")
        )
        set_key_in_dict_for_export(
            span_data,
            "capacityDetails/description",
            f.attribute("spans/0/capacityDetails/description"),
        )
        set_key_in_dict_for_export(
            span_data, "countries", f.attribute("spans/0/countries")
        )
        set_key_in_dict_for_export(
            span_data,
            "networkProviders/0/id",
            f.attribute("spans/0/networkProviders/0/id"),
        )
        networks[network_id]["spans"].append(span_data)
    # done
    return {"networks": [v for v in networks.values()]}
