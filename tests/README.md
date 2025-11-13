# Tests

## Setup

    pip install pytest

Delete the contents of `__init__.py` - when it's in this state you can't load the QGIS plugin, but if it's there tests break
Don't check in to git deleting that `__init__.py`!
TODO sort out that annoyance

## Run

    pytest tests

