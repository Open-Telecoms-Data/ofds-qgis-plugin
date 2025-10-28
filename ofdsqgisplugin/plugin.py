import json
import os
import shutil

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from .add_layers import add_layers
from .export import get_json
from .lib import find_layers

PLUGIN_DIR = os.path.dirname(__file__)


class OFDSQGISPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        # --------------------- Add Layers
        self.action_add_layers = QAction(
            QIcon(os.path.join(os.path.join(PLUGIN_DIR, "button_add.png"))),
            "Add Layers",
            self.iface.mainWindow(),
        )
        self.iface.addToolBarIcon(self.action_add_layers)
        self.action_add_layers.triggered.connect(self.add_layers)
        # --------------------- export JSON
        self.action_export_json = QAction(
            QIcon(os.path.join(os.path.join(PLUGIN_DIR, "button_export_json.png"))),
            "Export JSON",
            self.iface.mainWindow(),
        )
        self.iface.addToolBarIcon(self.action_export_json)
        self.action_export_json.triggered.connect(self.export_json)

    def unload(self):
        self.iface.removeToolBarIcon(self.action_add_layers)
        del self.action_add_layers
        self.iface.removeToolBarIcon(self.action_export_json)
        del self.action_export_json

    def add_layers(self):
        filename_details = QFileDialog.getSaveFileName(
            None, "Select output file ", "", "*.gpkg"
        )
        # catch cancel being pressed
        if not filename_details[0]:
            return
        # Get new filenme
        filename = filename_details[0] + ".gpkg"
        # Copy template to desired location
        shutil.copyfile(os.path.join(PLUGIN_DIR, "template.gpkg"), filename)
        # add layers
        add_layers(filename)

    def export_json(self):
        # get data and check it
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("We can not find OFDS layers to export")
            return
        # get filename
        filename_details = QFileDialog.getSaveFileName(
            None, "Select output file ", "", "*.json"
        )
        # catch cancel being pressed
        if not filename_details[0]:
            return
        # Get new filenme
        filename = filename_details[0] + ".json"
        # Make JSON
        data = get_json(layers)
        # Save JSON
        with open(filename, "w") as fp:
            json.dump(data, fp, indent=2)
