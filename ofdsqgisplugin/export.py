import copy
import json
import os
import uuid

from .python.export_to_json import export_callable_to_json


def get_json(layers):
    def callable(table_name):
        out = []
        for f in layers[table_name].getFeatures():
            data = {}
            for field_name in layers[table_name].fields().names():
                data[field_name] = f.attribute(field_name)
            out.append(data)
        return out

    return export_callable_to_json(callable)
