# How To build a new schema version in the plugin

## Building a new version from scratch

Create `schema_0_3` directories under both `buildofdsqgisplugin` and `ofdsqgisplugin`

Copy the Open codelists from the data standard under `buildofdsqgisplugin/schema_0_3/codelists/open`

Copy the Closed codelists from the data standard under `buildofdsqgisplugin/schema_0_3/codelists/closed`

Use CompileToJSONSchema tool ( https://github.com/OpenDataServices/compile-to-json-schema ) to compile one complete schema file:

    compiletojsonschema -c ~/work/openfibre-data-standard/codelists/closed/ ~/work/openfibre-data-standard/schema/network-schema.json  > ~/work/openfibre-qgis-plugin/buildofdsqgisplugin/schema_0_3/schema.json

Run the python to generate the Geopackage template

    python buildofdsqgisplugin/build_geopackage.py

## Credits

`buildofdsqgisplugin/empty.gpkg` comes from https://www.geopackage.org/guidance/getting-started.html#creating-a-geopackage
