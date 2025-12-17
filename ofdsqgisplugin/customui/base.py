import json
import os

PLUGIN_DIR = os.path.dirname(__file__)


def get_schema_information():
    with open(
        os.path.join(
            PLUGIN_DIR,
            "..",
            "schema_0_3",
            "schema_information.json",
        )
    ) as fp:
        return json.load(fp)
