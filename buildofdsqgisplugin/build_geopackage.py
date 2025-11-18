import csv
import json
import os
import shutil
import sqlite3

from jsonref import replace_refs

MAP_FIELD_TYPES_TO_SQLITE_TYPES = {"boolean": "int", "integer": "int", "number": "real"}

OBJECT_REFERENCES = {
    "Organisation reference": "organisations",
    "Phase reference": "phases"
}

STRING_REFERENCES = {
    "Start": "nodes",
    "End": "nodes"
}

GEOMETRY_TYPES = {
    "nodes": "POINT",
    "spans": "LINESTRING"
}

class Builder:

    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.connection = None
        self.cursor = None
        self.information_out = None

    def create_table(
        self,
        table_name,
        columns,
        geographic_type=None
    ):

        print(f"Creating table: {table_name} of geographic type {geographic_type} with columns: {[col for col in columns.keys()]}")

        cols_sql = [] 
        fks_sql = []
        for name, defn in columns.items():
            cols_sql.append(f'{name} {defn["type"]}')
            if defn.get("fk"):
                fks_sql.append(f'FOREIGN KEY ({name}) REFERENCES {defn["fk"]["table"]} ({defn["fk"]["column"]})')

            # Insert into gpkg_data_columns per
            # https://www.geopackage.org/spec/#extension_schema
            self.cursor.execute(f"""
            INSERT OR IGNORE INTO gpkg_data_columns (
                table_name, column_name, name, title, description, mime_type, constraint_name
            )
            VALUES (
                '{table_name}',
                '{name}',
                '{defn["title"]}',
                '{defn["title"]}',
                '{defn["description"].replace("'", "''")}',
                NULL,
                '{defn.get("enum", "NULL")}'
            );
            """)
 
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {}
                {}
            );
        """.format(
                table_name,
                "geom BLOB NOT NULL," if geographic_type else "",
                ",".join(cols_sql + fks_sql)
            )
        )


        self.cursor.execute(
            """
            INSERT OR IGNORE INTO gpkg_contents (table_name, data_type, identifier, srs_id)
            VALUES ('{}', '{}', '{}', 4326);
        """.format(
                table_name,
                "features" if geographic_type else "attributes",
                table_name,
            )
        )

        if geographic_type:
            self.cursor.execute(
                """
                INSERT INTO gpkg_geometry_columns (
                    table_name, column_name, geometry_type_name, srs_id, z, m
                ) VALUES ('{}', 'geom', '{}', 4326, 0, 0);
            """.format(
                    table_name, geographic_type
                )
            )

        self.information_out["tables"][table_name] = {
            "columns": columns,
            "geographic_type": geographic_type,
            "geographic_field": "geom",
        }

    def create_relationship(self, base_table, base_primary_column, related_table, related_primary_column, relationship_name):
        print(f"Creating relationship: {base_table} -> {related_table} ({relationship_name})")
        mapping_table_name = f"{base_table}_{relationship_name}_{related_table}_mapping"

        # Create mapping table per GeoPackage spec
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {mapping_table_name} (
            base_id TEXT NOT NULL,
            related_id TEXT NOT NULL,
            PRIMARY KEY (base_id, related_id),
            FOREIGN KEY (base_id) REFERENCES {base_table}({base_primary_column}),
            FOREIGN KEY (related_id) REFERENCES {related_table}({related_primary_column})
        );
        """)

        # Add mapping table to gpkg_extensions per GeoPackage spec
        self.cursor.execute(f"""
        INSERT OR IGNORE INTO gpkg_extensions (table_name, column_name, extension_name, definition, "scope")
        VALUES ('{mapping_table_name}', null, 'gpkg_related_tables','http://docs.opengeospatial.org/is/18-000/18-000.html', 'read-write');
        """)

        # Add the relationship to gpkgext_relations
        self.cursor.execute(f"""
        INSERT INTO gpkgext_relations (
            base_table_name,
            base_primary_column,
            related_table_name,
            related_primary_column,
            relation_type,
            mapping_table_name
        )
        VALUES  (
            '{base_table}',
            '{base_primary_column}',
            '{related_table}',
            '{related_primary_column}',
            '{relationship_name}',
            '{mapping_table_name}'
        );
        """)

    def create_codelist_table(self, codelist):
        print(f"Creating codelist table: {codelist}")
        columns = {
            "code": {
                "type": "TEXT",
                "title": "Code",
                "description": "Code"
            },
            "title": {
                "type": "TEXT",
                "title": "Title",
                "description": "Title"
            },
            "description": {
                "type": "TEXT",
                "title": "Description",
                "description": "Description"
            }
        }
        self.create_table(codelist.removesuffix(".csv").lower(), columns, None)

        for code in self.get_codes(codelist):
            self.cursor.execute(
                f"""
                INSERT INTO {codelist.removesuffix(".csv").lower()} (code, title, description) VALUES ('{code["Code"]}', '{code["Title"].replace("'", "''")}', '{code.get("Description", "").replace("'", "''")}');
                """
            )
            

    def get_codes(self, codelist):
        codes = []
        codelist_path = os.path.join(
            self.root_directory,
            "buildofdsqgisplugin",
            "schema_0_3",
            "codelists",
            codelist
        )
        with open(codelist_path, 'r') as codelist_file:
            codes = [code for code in csv.DictReader(codelist_file)]
        return codes
    
    def create_enum(self, name, values):
        print(f"Creating enum for {name} codelist")
        for value in values:
            desc_safe = f"{value["Title"]}: {value.get('Description', '')}".replace("'", "''")
            self.cursor.execute(f"""
                INSERT OR IGNORE INTO gpkg_data_column_constraints (
                constraint_name,
                constraint_type,
                value,
                description
                )
                VALUES (
                '{name}',
                'enum',
                '{value["Code"]}',
                '{desc_safe}'
                );
            """)

    def recurse(self, parent, schema):
        columns = {}

        for name, subschema in schema["properties"].items():
            name = name.lower()
            if parent:
                full_name = "_".join([parent, name])
            else:
                full_name = name

            # Avoid clash with id fields in GeoPackage spec
            if name == "id":
                name = "ofds_id"
            
            if subschema["type"] == "object":
                # Skip Geometry objects as they are handled in the create_table function
                if subschema["title"] == "Geometry":
                    continue
                # Replace singular OrganisationReference and PhaseReference reference objects with foreign key relationships
                elif subschema["title"] in OBJECT_REFERENCES:
                    columns[name] = {
                        "type": "INTEGER",
                        "title": subschema['title'],
                        "description": subschema['description'],
                        "fk": {
                            "table": OBJECT_REFERENCES[subschema['title']],
                            "column": "id"
                        }
                    }
                # Recurse through child properties
                else:
                    for col, defn in self.recurse(full_name, subschema).items():
                        columns["_".join([name, col])] = defn

            elif subschema["type"] == "array":
                if subschema["items"]["type"] == "object":
                    # Special case for objects that reference items in an array
                    if subschema["items"]["title"] in OBJECT_REFERENCES:
                        self.create_relationship(parent, "id", OBJECT_REFERENCES[subschema['items']['title']], "id", name)
                    else:
                        # Create a table from the object's properties and add foreign key to parent table
                        fk = {}
                        if parent:
                            fk[f"{parent}_id"] = {
                                    "type": "INTEGER",
                                    "title": f"{parent} ID",
                                    "description": f"Foreign key to {parent} table.",
                                    "fk": {
                                        "table": parent,
                                        "column": "id"
                                    }
                                }
                        self.create_table(full_name, fk | self.recurse(full_name, subschema['items']), GEOMETRY_TYPES.get(name))

                elif subschema["items"]["type"] in ["string", ["string"]]:
                    codelist_name = subschema["codelist"].removesuffix(".csv").lower()
                    self.create_codelist_table(subschema["codelist"])
                    self.create_relationship(parent, "id", codelist_name, "code", name)

            elif subschema["type"] == "string":
                if subschema.get("openCodelist"):
                    self.create_codelist_table(subschema["codelist"])
                    self.create_relationship(parent, "id", subschema["codelist"].removesuffix(".csv").lower(), "code", name)                
                else:
                    columns[name] = {
                        "title": subschema["title"],
                        "description": subschema["description"]
                    }
                    # Add foreign keys for Span.start and Span.end
                    if subschema["title"] in STRING_REFERENCES:
                        columns[name]["type"] = "INTEGER"
                        columns[name]["fk"] = {
                            "table": STRING_REFERENCES[subschema["title"]],
                            "column": "id"
                        }
                    else:
                        if subschema.get("codelist"):
                            codes = self.get_codes(subschema["codelist"])
                            self.create_enum(subschema["codelist"].removesuffix(".csv").lower(), codes)
                            columns[name]["enum"] = subschema["codelist"].removesuffix(".csv").lower()
                        columns[name]["type"] = "TEXT"

            elif subschema["type"] in ["boolean", "number", "integer"]:
                columns[name] = {
                    "type": MAP_FIELD_TYPES_TO_SQLITE_TYPES[subschema["type"]],
                    "title": subschema["title"],
                    "description": subschema["description"]
                }

        if parent is None:
            self.create_table("network", columns, None)

        return columns

    def go(self):
        # Load JSON Schema
        jsonschema_filename = os.path.join(
            self.root_directory,
            "buildofdsqgisplugin",
            "schema_0_3",
            "network-schema.json",
        )
        with open(jsonschema_filename) as fp:
            jsonschema = json.load(fp)

        # Dereference schema
        jsonschema = replace_refs(jsonschema)

        # Create Tables
        # Copy GeoPackage
        sqlite_filename = os.path.join(
            self.root_directory,
            "ofdsqgisplugin",
            "schema_0_3",
            "geopackage.gpkg",
        )
        shutil.copyfile(
            os.path.join(
                self.root_directory,
                "buildofdsqgisplugin",
                "empty.gpkg",
            ),
            sqlite_filename,
        )
        # Setup
        self.connection = sqlite3.connect(sqlite_filename)
        self.cursor = self.connection.cursor()
        self.information_out = {"tables": {}}

        # Create extension tables
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpkgext_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, base_table_name TEXT NOT NULL, base_primary_column TEXT NOT NULL, related_table_name TEXT NOT NULL, related_primary_column TEXT NOT NULL, relation_type TEXT NOT NULL, mapping_table_name TEXT UNIQUE
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpkg_data_columns (
            table_name TEXT NOT NULL, column_name TEXT NOT NULL, name TEXT, title TEXT, description TEXT, mime_type TEXT, constraint_name TEXT,
            CONSTRAINT pk_gdc PRIMARY KEY (table_name, column_name)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpkg_data_column_constraints (
            constraint_name TEXT NOT NULL, constraint_type TEXT NOT NULL, value TEXT, min NUMERIC, min_is_inclusive BOOLEAN, max NUMERIC, max_is_inclusive BOOLEAN, description TEXT, CONSTRAINT gdcc_ntv UNIQUE (constraint_name, constraint_type, value)
        );
        """)

        # Register extensions
        self.cursor.execute("INSERT OR IGNORE INTO gpkg_extensions (table_name, column_name, extension_name, definition, scope) VALUES ('gpkgext_relations', NULL, 'gpkg_related_tables','http://docs.opengeospatial.org/is/18-000/18-000.html', 'read-write');")
        self.cursor.execute("INSERT OR IGNORE INTO gpkg_extensions (table_name, column_name, extension_name, definition, scope) VALUES ('gpkg_data_columns', NULL, 'gpkg_schema','http://www.geopackage.org/spec120/#extension_schema', 'read-write');")
        self.cursor.execute("INSERT OR IGNORE INTO gpkg_extensions (table_name, column_name, extension_name, definition, scope) VALUES ('gpkg_data_column_constraints', NULL, 'gpkg_schema','http://www.geopackage.org/spec120/#extension_schema', 'read-write');")
        self.connection.commit()        
        
        # Create tables from schema

        self.recurse(None, jsonschema)

        # Wrapup
        self.connection.commit()
        schema_information_json_filename = os.path.join(
            self.root_directory,
            "ofdsqgisplugin",
            "schema_0_3",
            "schema_information.json",
        )
        with open(schema_information_json_filename, "w") as fp:
            json.dump(self.information_out, fp, indent=2)


if __name__ == "__main__":
    builder = Builder(
        root_directory=os.path.realpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
        ),
    )
    builder.go()
