# How To build a new schema version in the plugin

## Building a new version from scratch

Create `schema_0_4` directory under `ofdsqgisplugin`

Run the python to generate the Geopackage template

    python ../open-fibre-data-standard/buildofdsgeopackage.py --output-directory ofdsqgisplugin/schema_0_4 --write-schema-information-json

## Not everything is built from schema

Some things are hard coded into various places, and if big changes are made to the schema will need to be changed too. Basically, test fully!

Some places:

* buildofdsqgisplugin/build_geopackage.py has the variables MAPPING_FOREIGN_KEY_NAMES_TO_LAYERS and MAPPING_MANY_TO_MANY_KEY_NAMES_TO_LAYERS
* buildofdsqgisplugin/build_geopackage.py has hard coded tables in the go() function
* ofdsqgisplugin/python/export_to_json.py has hard coded table names in
* ofdsqgisplugin/python/import_from_json.py has hard coded table names in

## Credits

`buildofdsqgisplugin/empty.gpkg` comes from https://www.geopackage.org/guidance/getting-started.html#creating-a-geopackage
