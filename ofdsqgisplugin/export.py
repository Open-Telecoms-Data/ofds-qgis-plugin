import copy
import json
import os
import uuid

from .python.export_to_json import export_callable_to_json

PLUGIN_DIR = os.path.dirname(__file__)


def get_json(layers):
    # Get Information
    with open(
        os.path.join(
            PLUGIN_DIR,
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        schema_information = json.load(fp)

    # Work
    def callable(table_name):
        out = []
        for f in layers[table_name].getFeatures():
            data = {}
            for field_name in layers[table_name].fields().names():
                data[field_name] = f.attribute(field_name)
            if schema_information["tables"][table_name]["geographic_field"]:
                data["geom"] = f.geometry().asJson()
            out.append(data)
        return out

    return export_callable_to_json(callable)
