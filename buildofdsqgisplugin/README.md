# How To build a new schema version in the plugin

## Building a new version from scratch

Create `schema_0_3` directories under both `buildofdsqgisplugin` and `ofdsqgisplugin`

Copy all the codelists from the data standard under `ofdsqgisplugin/codelists`

Use CompileToJSONSchema tool ( https://github.com/OpenDataServices/compile-to-json-schema ) to compile one complete schema file:

    compiletojsonschema -c ~/work/openfibre-data-standard/codelists/closed/ ~/work/openfibre-data-standard/schema/network-schema.json  > ~/work/openfibre-qgis-plugin/buildofdsqgisplugin/schema_0_3/schema.json

Use FlattenTool ( https://github.com/OpenDataServices/flatten-tool) to turn that schema file into CSV's:

    cd ~/work/openfibre-qgis-plugin/buildofdsqgisplugin/schema_0_3/
    flatten-tool create-template -s schema.json -f csv -m networks -o csv --truncation-length 99

**Hand Edit** the contents of the `buildofdsqgisplugin/schema_0_3/csv` directory and remove any tables we don't want as tables in QGIS.

* Delete links CSV file

Run the Python to start generating the schema information we need

    VERSION_MAJOR=0 VERSION_MINOR=3 python buildofdsqgisplugin/build_schema_information.py

**Hand Edit** the contents of the `ofdsqgisplugin/schema_0_3/schema_information.json` file and set up the information we need.

* Delete any geometry fields, and instead set `geometry_type` on that table
* remove the CRS stuff from networks
* set field types and any options they need
* ename field names

Run the python to generate the Geopackage template

    VERSION_MAJOR=0 VERSION_MINOR=3 python buildofdsqgisplugin/build_geopackage.py

## Credits

`buildofdsqgisplugin/empty.gpkg` comes from https://www.geopackage.org/guidance/getting-started.html#creating-a-geopackage


## Linting

After hand editing `ofdsqgisplugin/schema_0_3/schema_information.json`, lint it with `jq`:

    cat ofdsqgisplugin/schema_0_3/schema_information.json | jq "." > ofdsqgisplugin/schema_0_3/schema_information2.json
    mv ofdsqgisplugin/schema_0_3/schema_information2.json ofdsqgisplugin/schema_0_3/schema_information.json
