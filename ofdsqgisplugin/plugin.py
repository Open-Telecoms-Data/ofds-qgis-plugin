import json
import os
import shutil

from qgis.core import QgsProject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from .add_layers import add_layers
from .export import get_json
from .import_data import import_json
from .lib import find_layers
from .validate import ValidateDialog

PLUGIN_DIR = os.path.dirname(__file__)

CUSTOM_UI_FEATURE_FLAG = bool(
    int(os.environ.get("OPENFIBRE_QGIS_PLUGIN_CUSTOM_UI_FEATURE_FLAG", "0"))
)

if CUSTOM_UI_FEATURE_FLAG:
    from .customui.home import HomeDialog
    from .customui.new_thing_select_network import NewThingSelectNetworkDialog


class OFDSQGISPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.validate_dialog = ValidateDialog()
        if CUSTOM_UI_FEATURE_FLAG:
            self.custom_ui_home = HomeDialog()
        self.currently_importing = False

    def initGui(self):
        # --------------------- Add Layers
        self.action_add_layers = QAction(
            QIcon(os.path.join(os.path.join(PLUGIN_DIR, "button_add.svg"))),
            "Create OFDS GeoPackage",
            self.iface.mainWindow(),
        )
        self.iface.addToolBarIcon(self.action_add_layers)
        self.action_add_layers.triggered.connect(self.add_layers)
        # --------------------- import JSON
        self.action_import_json = QAction(
            QIcon(os.path.join(os.path.join(PLUGIN_DIR, "button_import_json.svg"))),
            "Import JSON",
            self.iface.mainWindow(),
        )
        self.iface.addToolBarIcon(self.action_import_json)
        self.action_import_json.triggered.connect(self.import_json)
        # --------------------- validate
        self.action_validate = QAction(
            QIcon(os.path.join(os.path.join(PLUGIN_DIR, "button_validate.svg"))),
            "Validate",
            self.iface.mainWindow(),
        )
        self.iface.addToolBarIcon(self.action_validate)
        self.action_validate.triggered.connect(self.validate)
        # --------------------- export JSON
        self.action_export_json = QAction(
            QIcon(os.path.join(os.path.join(PLUGIN_DIR, "button_export_json.svg"))),
            "Export JSON",
            self.iface.mainWindow(),
        )
        self.iface.addToolBarIcon(self.action_export_json)
        self.action_export_json.triggered.connect(self.export_json)
        # --------------------- custom ui
        if CUSTOM_UI_FEATURE_FLAG:
            self.action_custom_ui = QAction(
                QIcon(os.path.join(os.path.join(PLUGIN_DIR, "button_custom_ui.svg"))),
                "Open UI",
                self.iface.mainWindow(),
            )
            self.iface.addToolBarIcon(self.action_custom_ui)
            self.action_custom_ui.triggered.connect(self.custom_ui)

    def unload(self):
        # --------------------- Add Layers
        self.iface.removeToolBarIcon(self.action_add_layers)
        del self.action_add_layers
        # --------------------- import JSON
        self.iface.removeToolBarIcon(self.action_import_json)
        del self.action_import_json
        # --------------------- validate
        self.iface.removeToolBarIcon(self.action_validate)
        del self.action_validate
        self.validate_dialog.close()
        del self.validate_dialog
        # --------------------- export JSON
        self.iface.removeToolBarIcon(self.action_export_json)
        del self.action_export_json
        # --------------------- custom ui
        if CUSTOM_UI_FEATURE_FLAG:
            self.iface.removeToolBarIcon(self.action_custom_ui)
            del self.action_custom_ui
            self.custom_ui_home.close()
            del self.custom_ui_home

    def add_layers(self):
        # check projection
        # The data standard says it should be OGC:CRS84
        # https://standard.ofds.info/en/0.1-dev/reference/schema.html?highlight=wgs84#coordinatereferencesystem
        if QgsProject.instance().crs().authid() not in ["OGC:CRS84", "EPSG:4326"]:
            self.iface.messageBar().pushMessage(
                "Can only use OFDS with projects in the OGC:CRS84 or EPSG:4326 coordinate reference system (CRS). Please change your coordinate reference system."
            )
            return
        # check already has layers
        layers = find_layers()
        if layers:
            self.iface.messageBar().pushMessage("This project already has OFDS layers")
            return
        # get filename
        filename_details = QFileDialog.getSaveFileName(
            None, "Select output file ", "", "*.gpkg"
        )
        # catch cancel being pressed
        if not filename_details[0]:
            return
        # Get new filenme
        filename = filename_details[0] + (
            "" if filename_details[0].endswith(".gpkg") else ".gpkg"
        )
        # Copy template to desired location
        shutil.copyfile(
            os.path.join(PLUGIN_DIR, "schema_0_3", "geopackage.gpkg"), filename
        )
        # add layers
        add_layers(filename, self, custom_ui=CUSTOM_UI_FEATURE_FLAG)

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
        filename = filename_details[0] + (
            "" if filename_details[0].endswith(".json") else ".json"
        )
        # Make JSON
        data = get_json(layers)
        # Save JSON
        with open(filename, "w") as fp:
            json.dump(data, fp, indent=2)

    def import_json(self):
        self.currently_importing = True
        # check
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Create OFDS GeoPackage first")
            return
        # get filename
        filename_details = QFileDialog.getOpenFileName(
            None, "Select input JSON file ", "", "*.json"
        )
        # catch cancel being pressed
        if not filename_details[0]:
            return
        # Get new filenme
        filename = filename_details[0]
        # import JSON
        with open(filename) as fp:
            data = json.load(fp)
        import_json(layers, data)
        # wrap up
        self.currently_importing = False

    def validate(self):
        # check
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Create OFDS GeoPackage first")
            return
        # Validate
        self.validate_dialog.validate(layers, self.iface.messageBar())

    def custom_ui(self):
        # check
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Create OFDS GeoPackage first")
            return
        # Validate
        self.custom_ui_home.start()

    def on_node_feature_added(self, fid):
        if not self.currently_importing:
            self.node_feature_added_dialog = NewThingSelectNetworkDialog("nodes", fid)
            self.node_feature_added_dialog.start()

    def on_span_feature_added(self, fid):
        if not self.currently_importing:
            self.span_feature_added_dialog = NewThingSelectNetworkDialog("spans", fid)
            self.span_feature_added_dialog.start()
