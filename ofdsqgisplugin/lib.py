from PyQt5.QtCore import QDate, Qt
from qgis.core import QgsProject, QgsVectorLayer


def find_layers():
    layers = {
        "networks": None,
        "nodes": None,
        "spans": None,
        "contracts": None,
        "phases": None,
        "spans_networkProviders": None,
        "phases_funders": None,
        "organisations": None,
        "nodes_networkProviders": None,
        "nodes_internationalConnections": None,
        "links": None,
        # "contracts_relatedPhases": None,
        # "contracts_documents": None,
    }
    for k, v in QgsProject.instance().mapLayers().items():
        if isinstance(v, QgsVectorLayer):
            if k.startswith("Networks_"):
                layers["networks"] = v
            elif k.startswith("Nodes_"):
                layers["nodes"] = v
            elif k.startswith("Spans_"):
                layers["spans"] = v
            elif k.startswith("contracts_"):
                layers["contracts"] = v
            elif k.startswith("Phases_"):
                layers["phases"] = v
            elif k.startswith("spans_networkProviders_"):
                layers["spans_networkProviders"] = v
            elif k.startswith("phases_funders_"):
                layers["phases_funders"] = v
            elif k.startswith("organisations_"):
                layers["organisations"] = v
            elif k.startswith("nodes_networkProviders_"):
                layers["nodes_networkProviders"] = v
            elif k.startswith("nodes_internationalConnections_"):
                layers["nodes_internationalConnections"] = v
            elif k.startswith("links_"):
                layers["links"] = v
            # elif k.startswith("contracts_relatedPhases"):
            #    layers["contracts_relatedPhases"] = v
            # elif k.startswith("contracts_documents"):
            #    layers["contracts_documents"] = v
    # If any of the layers are missing, return None.
    # That way downstream code can raise an alert on a simple "if" check
    # and can then trust all layers are present
    return None if [k for k, v in layers.items() if not v] else layers


def set_key_in_dict_for_export(data, key, value):
    if not value:
        return
    key_bits = key.split("/")
    final_key = key_bits.pop(-1)
    for key_bit in key_bits:
        if key_bit in data:
            data = data[key_bit]
        else:
            data[key_bit] = {}
            data = data[key_bit]
    if isinstance(value, QDate):
        data[final_key] = value.toString(Qt.ISODate)
    else:
        data[final_key] = value
