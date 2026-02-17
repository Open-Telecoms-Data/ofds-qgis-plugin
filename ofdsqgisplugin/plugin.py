import json
import os
import shutil

from qgis.core import QgsProject, QgsMapLayer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QLabel

from .add_layers import add_layers, move_basemap_to_bottom, ensure_layer_order
from .export import get_json
from .import_data import import_json
from .lib import find_layers
from .validate import ValidateDialog
from .health_check import HealthCheckDialog
from .locator import LocatorDialog
from .about_dialog import AboutDialog

PLUGIN_DIR = os.path.dirname(__file__)

CUSTOM_UI_FEATURE_FLAG = bool(
    int(os.environ.get("OPENFIBRE_QGIS_PLUGIN_CUSTOM_UI_FEATURE_FLAG", "0"))
)

if CUSTOM_UI_FEATURE_FLAG:
    from .customui.home import HomeDialog
    from .customui.new_thing_select_network import NewThingSelectNetworkDialog
    from .customui.table_edit import TableEditDialog


class OFDSQGISPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.validate_dialog = ValidateDialog()
        self.health_check_dialog = HealthCheckDialog()
        self.locator_dialog = LocatorDialog(iface)
        self.about_dialog = AboutDialog()
        if CUSTOM_UI_FEATURE_FLAG:
            self.custom_ui_home = HomeDialog()
        self.currently_importing = False
        self._layer_added_connection = None  # Track connection for cleanup

    def initGui(self):
        # --------------------- Create custom OFDS toolbar
        self.toolbar = self.iface.addToolBar("Open Fibre Data Standard")
        self.toolbar.setObjectName("OFDSToolbar")
        
        # Add OFDS label/branding to the left
        self.ofds_label = QLabel("  OFDS  ")
        self.ofds_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11px;
                color: white;
                padding: 2px 8px;
                background-color: #0C1031;
                border: 1px solid #0C1031;
                border-radius: 3px;
                margin: 2px;
            }
        """)
        self.ofds_label.setToolTip("Open Fibre Data Standard")
        self.toolbar.addWidget(self.ofds_label)
        
        # Add separator after label
        self.toolbar.addSeparator()
        
        # --------------------- Add Layers
        self.action_add_layers = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_add.svg")),
            "Create OFDS GeoPackage",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_add_layers)
        self.action_add_layers.triggered.connect(self.add_layers)
        
        # --------------------- import JSON
        self.action_import_json = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_import_json.svg")),
            "Import JSON",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_import_json)
        self.action_import_json.triggered.connect(self.import_json)
        
        # --------------------- validate
        self.action_validate = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_validate.svg")),
            "Validate",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_validate)
        self.action_validate.triggered.connect(self.validate)
        
        # --------------------- health check
        self.action_health_check = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_health_check.svg")),
            "Health Check",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_health_check)
        self.action_health_check.triggered.connect(self.health_check)
        
        # --------------------- locator
        self.action_locator = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_locator.svg")),
            "Location Finder",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_locator)
        self.action_locator.triggered.connect(self.show_locator)
        
        # --------------------- toggle labels
        self.action_toggle_labels = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_labels.svg")),
            "Toggle Labels",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_toggle_labels)
        self.action_toggle_labels.triggered.connect(self.toggle_labels)
        
        # --------------------- export JSON
        self.action_export_json = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_export_json.svg")),
            "Export JSON",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_export_json)
        self.action_export_json.triggered.connect(self.export_json)
        
        # --------------------- export GeoPackage
        self.action_export_gpkg = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_export_gpkg.svg")),
            "Export to GeoPackage",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_export_gpkg)
        self.action_export_gpkg.triggered.connect(self.export_geopackage)
        
        # --------------------- custom ui
        if CUSTOM_UI_FEATURE_FLAG:
            self.action_custom_ui = QAction(
                QIcon(os.path.join(PLUGIN_DIR, "button_custom_ui.svg")),
                "Open UI",
                self.iface.mainWindow(),
            )
            self.toolbar.addAction(self.action_custom_ui)
            self.action_custom_ui.triggered.connect(self.custom_ui)
            
        # --------------------- custom ui selected features
        if CUSTOM_UI_FEATURE_FLAG:
            self.action_custom_ui_selected_features = QAction(
                QIcon(os.path.join(PLUGIN_DIR, "button_custom_ui_selected_features.svg")),
                "Open UI on selected features",
                self.iface.mainWindow(),
            )
            self.toolbar.addAction(self.action_custom_ui_selected_features)
            self.action_custom_ui_selected_features.triggered.connect(
                self.custom_ui_selected_features
            )
        
        # --------------------- About/Info button (at the end with separator)
        self.toolbar.addSeparator()
        self.action_about = QAction(
            QIcon(os.path.join(PLUGIN_DIR, "button_info.svg")),
            "About OFDS Plugin",
            self.iface.mainWindow(),
        )
        self.toolbar.addAction(self.action_about)
        self.action_about.triggered.connect(self.show_about)
        
        # --------------------- Layer ordering: keep basemaps at bottom
        # Connect to layerWasAdded signal to auto-reorder when new layers are added
        self._layer_added_connection = QgsProject.instance().layerWasAdded.connect(
            self.on_layer_added
        )

    def unload(self):
        # --------------------- Remove all actions from toolbar
        self.toolbar.removeAction(self.action_add_layers)
        del self.action_add_layers
        
        self.toolbar.removeAction(self.action_import_json)
        del self.action_import_json
        
        self.toolbar.removeAction(self.action_validate)
        del self.action_validate
        self.validate_dialog.close()
        del self.validate_dialog
        
        self.toolbar.removeAction(self.action_health_check)
        del self.action_health_check
        self.health_check_dialog.close()
        del self.health_check_dialog
        
        self.toolbar.removeAction(self.action_locator)
        del self.action_locator
        self.locator_dialog.close()
        del self.locator_dialog
        
        self.toolbar.removeAction(self.action_toggle_labels)
        del self.action_toggle_labels
        
        self.toolbar.removeAction(self.action_export_json)
        del self.action_export_json
        
        self.toolbar.removeAction(self.action_export_gpkg)
        del self.action_export_gpkg
        
        # --------------------- custom ui
        if CUSTOM_UI_FEATURE_FLAG:
            self.toolbar.removeAction(self.action_custom_ui)
            del self.action_custom_ui
            self.custom_ui_home.close()
            del self.custom_ui_home
            
        # --------------------- custom ui on selected features
        if CUSTOM_UI_FEATURE_FLAG:
            self.toolbar.removeAction(self.action_custom_ui_selected_features)
            del self.action_custom_ui_selected_features
        
        # --------------------- About dialog
        self.toolbar.removeAction(self.action_about)
        del self.action_about
        self.about_dialog.close()
        del self.about_dialog
        
        # --------------------- Remove OFDS label and toolbar
        del self.ofds_label
        del self.toolbar
        
        # --------------------- Layer ordering connection cleanup
        if self._layer_added_connection:
            try:
                QgsProject.instance().layerWasAdded.disconnect(self.on_layer_added)
            except TypeError:
                pass  # Already disconnected
            self._layer_added_connection = None

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

    def export_geopackage(self):
        """Export OFDS layers to a new GeoPackage file."""
        from .export_gpkg import export_to_geopackage
        
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("No OFDS layers found to export")
            return
        
        export_to_geopackage(layers, self.iface)

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

    def health_check(self):
        # check
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Create OFDS GeoPackage first")
            return
        # Run health check
        self.health_check_dialog.start(layers)

    def show_locator(self):
        """Show the location finder dialog."""
        self.locator_dialog.show()

    def show_about(self):
        """Show the About dialog with plugin information."""
        self.about_dialog.show()

    def toggle_labels(self):
        """Toggle labels on/off for OFDS layers (nodes and spans)."""
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Create OFDS GeoPackage first")
            return
        
        # Check current state using nodes layer as reference
        nodes_layer = layers.get('nodes', None)
        if nodes_layer:
            # Toggle to opposite of current state
            new_state = not nodes_layer.labelsEnabled()
            
            # Apply to both nodes and spans
            for layer_name in ['nodes', 'spans']:
                if layer_name in layers:
                    layers[layer_name].setLabelsEnabled(new_state)
                    layers[layer_name].triggerRepaint()
            
            # Show status message
            status = "enabled" if new_state else "disabled"
            self.iface.messageBar().pushMessage(f"Labels {status}", duration=2)

    def custom_ui(self):
        # check
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Create OFDS GeoPackage first")
            return
        # Validate
        self.custom_ui_home.start()

    def custom_ui_selected_features(self):
        # check
        layers = find_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Create OFDS GeoPackage first")
            return
        # find features, open edit
        self.custom_ui_selected_features_dialogs = []
        for table_name in ["nodes", "spans"]:
            for feature in layers[table_name].selectedFeatures():
                # Get feature Data
                feature_data = {}
                for field_name in layers[table_name].fields().names():
                    feature_data[field_name] = feature.attribute(field_name)
                # Get Network data
                network_data = {
                    "id": feature_data["network_id"]
                }  # TODO we might need more fields like this?
                # Open Dialog
                ted = TableEditDialog(table_name)
                ted.start_edit(feature_data, network_data)
                self.custom_ui_selected_features_dialogs.append(ted)
        # TODO if no features selected, show a friendly message to the user

    def on_node_feature_added(self, fid):
        if not self.currently_importing:
            self.node_feature_added_dialog = NewThingSelectNetworkDialog("nodes", fid)
            self.node_feature_added_dialog.start()

    def on_span_feature_added(self, fid):
        if not self.currently_importing:
            self.span_feature_added_dialog = NewThingSelectNetworkDialog("spans", fid)
            self.span_feature_added_dialog.start()

    def on_layer_added(self, layer):
        """Handle layer added event to maintain proper layer ordering.
        
        When a new layer is added (especially basemap/raster layers),
        this ensures:
        1. Basemap layers are moved to the bottom
        2. The Open Fibre group stays at the top
        
        Args:
            layer: QgsMapLayer - the layer that was added
        """
        # Only process if we have OFDS layers in the project
        layers = find_layers()
        if not layers:
            return
        
        # Move basemap layers to bottom and keep OFDS group at top
        move_basemap_to_bottom(layer)
