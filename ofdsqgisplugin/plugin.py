import os
import shutil

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from .add_layers import add_layers

PLUGIN_DIR = os.path.dirname(__file__)


class OFDSQGISPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        # --------------------- Add Layers
        icon = os.path.join(os.path.join(PLUGIN_DIR, "button_add.png"))
        self.action_add_layers = QAction(
            QIcon(icon), "Add Layers", self.iface.mainWindow()
        )
        self.iface.addToolBarIcon(self.action_add_layers)
        self.action_add_layers.triggered.connect(self.add_layers)

    def unload(self):
        self.iface.removeToolBarIcon(self.action_add_layers)
        del self.action_add_layers

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
