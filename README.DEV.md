# How to develop Open Fibre Data Standard (OFDS) QGIS Plugin

## Sections of the repository

### buildofdsqgisplugin package

This code is not used directly by QGIS.

It is run by developers to take the standard (in JSON schema) and build a geopackage and JSON information file in the ofdsqgisplugin package.

See the README there for how it works.

### ofdsqgisplugin package

The actual python code and resources that is used by QGIS.

### ofdsqgisplugin.libcoveofds package

This is Python code that is copied from https://github.com/Open-Telecoms-Data/lib-cove-ofds with only minor changes.

### ofdsqgisplugin.python package

Primarily, it's a geopackage <-> JSON data importer/exporter

Nothing in this package should import any QGIS code.

This way,

* it can be tested by pytest without QGIS.
* the code can be used elsewhere later.

## tests

Contains Python tests.

See the README there for how it works.

## How to develop in QGIS

Check the repository out.

In QGIS, use the *Settings -> User Profiles -> Open active profile folder* option to find out where your profile folder is.

In that directory, go into `python/plugins` and create a soft sym link for a directory called `ofds` to the repository directory.

In QGIS, go to *Plugins -> Manage and install plugins* and activate the plugin.

You'll also want to search for the following plugins and activate them:

* *First Aid* - Get a nice debug page when your python crashes
* *Plugin Reloader* - Easy button to reload plugin without restarting QGIS

## Uploading a new version to the plugin repository

* Download the zip from https://github.com/Open-Telecoms-Data/ofds-qgis-plugin/archive/refs/heads/main.zip
* Edit the zip to have `ofds_studio` as the top level directory (any valid python module name should work, but dashes are not allowed)
* Test the edited zip in QGIS
* Upload the zip to https://plugins.qgis.org/plugins/ofds_studio/version/add/
* The plugin should contain a Changelog, so you don't need to fill one here
* You should be able to check off everything in the Pre-upload Checklist (true as of 2026-05-06, they may add extra)

## Linting

Please black and isort the python code - we don't have C.I. set up for this yet.


