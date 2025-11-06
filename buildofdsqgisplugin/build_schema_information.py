import csv
import json
import os


def go(root_directory, version_major, version_minor):
    out = {}
    csv_dir = os.path.join(
        root_directory,
        "buildofdsqgisplugin",
        "schema_{}_{}".format(version_major, version_minor),
        "csv",
    )
    for filename in os.listdir(csv_dir):
        if filename.endswith(".csv"):
            with open(os.path.join(csv_dir, filename)) as csvfile:
                csvreader = csv.reader(csvfile)
                csvline = next(csvreader)
                out[filename[:-4]] = {
                    "geometry_type": "",
                    "fields": [
                        {
                            "name": "ofds_id" if x == "id" else x,
                            "alias": "",
                            "comment": "",
                            "type": "",
                        }
                        for x in csvline
                    ],
                }
    with open(
        os.path.join(
            root_directory,
            "ofdsqgisplugin",
            "schema_{}_{}".format(version_major, version_minor),
            "schema_information.json",
        ),
        "w",
    ) as fp:
        json.dump(out, fp, indent=4)


if __name__ == "__main__":
    go(
        root_directory=os.path.realpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
        ),
        version_major=os.getenv("VERSION_MAJOR"),
        version_minor=os.getenv("VERSION_MINOR"),
    )
