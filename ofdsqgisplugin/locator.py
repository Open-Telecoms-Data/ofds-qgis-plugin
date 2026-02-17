"""
Location Finder Dialog for OFDS QGIS Plugin.

Provides tools for finding locations by coordinates or address search.
"""

import json
import urllib.request
import urllib.parse

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QTabWidget, QWidget, QMessageBox,
    QFormLayout, QDoubleSpinBox, QComboBox
)
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsPointXY, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsProject
)


class LocatorDialog(QDialog):
    """Dialog for finding locations by coordinates or address."""
    
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("OFDS Location Finder")
        self.resize(450, 250)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget for different input methods
        tabs = QTabWidget()
        
        # === Coordinates Tab ===
        coord_tab = QWidget()
        coord_layout = QVBoxLayout(coord_tab)
        
        # Instructions
        coord_label = QLabel("Enter coordinates in decimal degrees (WGS84):")
        coord_layout.addWidget(coord_label)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Latitude input
        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90.0, 90.0)
        self.lat_input.setDecimals(6)
        self.lat_input.setValue(0.0)
        self.lat_input.setSpecialValueText("")
        form_layout.addRow("Latitude:", self.lat_input)
        
        # Longitude input
        self.lon_input = QDoubleSpinBox()
        self.lon_input.setRange(-180.0, 180.0)
        self.lon_input.setDecimals(6)
        self.lon_input.setValue(0.0)
        self.lon_input.setSpecialValueText("")
        form_layout.addRow("Longitude:", self.lon_input)
        
        # Zoom level
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems([
            "City level (1:100000)",
            "District level (1:50000)",
            "Neighborhood level (1:10000)",
            "Street level (1:5000)",
            "Building level (1:1000)"
        ])
        self.zoom_combo.setCurrentIndex(3)  # Default to street level
        form_layout.addRow("Zoom to:", self.zoom_combo)
        
        coord_layout.addLayout(form_layout)
        
        # Go button
        go_coord_btn = QPushButton("Go to Coordinates")
        go_coord_btn.clicked.connect(self._go_to_coordinates)
        coord_layout.addWidget(go_coord_btn)
        
        # Add stretch to push everything up
        coord_layout.addStretch()
        
        tabs.addTab(coord_tab, "Coordinates")
        
        # === Address Tab ===
        addr_tab = QWidget()
        addr_layout = QVBoxLayout(addr_tab)
        
        # Instructions
        addr_label = QLabel("Search for a location by address or place name:")
        addr_layout.addWidget(addr_label)
        
        # Address input
        self.addr_input = QLineEdit()
        self.addr_input.setPlaceholderText("e.g., 123 Main St, City, Country")
        self.addr_input.returnPressed.connect(self._search_address)
        addr_layout.addWidget(self.addr_input)
        
        # Search button
        search_btn = QPushButton("Search Address")
        search_btn.clicked.connect(self._search_address)
        addr_layout.addWidget(search_btn)
        
        # Result label
        self.addr_result = QLabel("")
        self.addr_result.setWordWrap(True)
        self.addr_result.setStyleSheet("color: #666; font-style: italic;")
        addr_layout.addWidget(self.addr_result)
        
        # Note about service
        note_label = QLabel(
            "<small>Address search powered by OpenStreetMap Nominatim.<br>"
            "Please respect their usage policy.</small>"
        )
        note_label.setStyleSheet("color: #999;")
        addr_layout.addWidget(note_label)
        
        # Add stretch to push everything up
        addr_layout.addStretch()
        
        tabs.addTab(addr_tab, "Address Search")
        
        layout.addWidget(tabs)
        
        # === Bottom buttons ===
        btn_layout = QHBoxLayout()
        
        # Get current location button
        get_current_btn = QPushButton("Get Map Center")
        get_current_btn.clicked.connect(self._get_map_center)
        btn_layout.addWidget(get_current_btn)
        
        btn_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _get_zoom_scale(self):
        """Get the zoom scale based on combo box selection."""
        scales = [100000, 50000, 10000, 5000, 1000]
        return scales[self.zoom_combo.currentIndex()]
    
    def _go_to_coordinates(self):
        """Pan map to entered coordinates."""
        lat = self.lat_input.value()
        lon = self.lon_input.value()
        
        # Basic validation
        if lat == 0.0 and lon == 0.0:
            reply = QMessageBox.question(
                self, "Confirm Location",
                "Go to coordinates (0, 0)? This is in the Atlantic Ocean.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Transform to project CRS if needed
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        dest_crs = QgsProject.instance().crs()
        
        if source_crs != dest_crs:
            transform = QgsCoordinateTransform(
                source_crs, dest_crs, QgsProject.instance()
            )
            point = transform.transform(QgsPointXY(lon, lat))
        else:
            point = QgsPointXY(lon, lat)
        
        # Pan to location
        canvas = self.iface.mapCanvas()
        canvas.setCenter(point)
        canvas.zoomScale(self._get_zoom_scale())
        canvas.refresh()
        
        self.addr_result.setText(f"Moved to: {lat:.6f}, {lon:.6f}")
    
    def _search_address(self):
        """Search for address using Nominatim."""
        address = self.addr_input.text().strip()
        if not address:
            self.addr_result.setText("Please enter an address to search.")
            return
        
        self.addr_result.setText("Searching...")
        self.addr_result.repaint()  # Force UI update
        
        # Build Nominatim URL
        # Note: In production, respect Nominatim usage policy
        # Consider using a local geocoding service for heavy usage
        encoded_address = urllib.parse.quote(address)
        url = (
            f"https://nominatim.openstreetmap.org/search?"
            f"q={encoded_address}&format=json&limit=1"
        )
        
        try:
            # Create request with proper User-Agent (required by Nominatim)
            headers = {
                'User-Agent': 'OFDS-QGIS-Plugin/1.0 (https://github.com/Open-Telecoms-Data/ofds-qgis-plugin)'
            }
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                display_name = data[0].get('display_name', address)
                
                # Update coordinate inputs
                self.lat_input.setValue(lat)
                self.lon_input.setValue(lon)
                
                # Truncate display name if too long
                if len(display_name) > 80:
                    display_name = display_name[:77] + "..."
                
                self.addr_result.setText(f"Found: {display_name}")
                self.addr_result.setStyleSheet("color: #228B22; font-style: italic;")  # Green
                
                # Pan to location
                self._go_to_coordinates()
            else:
                self.addr_result.setText("No results found. Try a different search term.")
                self.addr_result.setStyleSheet("color: #B22222; font-style: italic;")  # Red
        
        except urllib.error.URLError as e:
            self.addr_result.setText(f"Network error: Could not connect to search service.")
            self.addr_result.setStyleSheet("color: #B22222; font-style: italic;")
        except Exception as e:
            self.addr_result.setText(f"Search error: {str(e)}")
            self.addr_result.setStyleSheet("color: #B22222; font-style: italic;")
    
    def _get_map_center(self):
        """Get the current map center coordinates."""
        canvas = self.iface.mapCanvas()
        center = canvas.center()
        
        # Transform to WGS84 if needed
        project_crs = QgsProject.instance().crs()
        wgs84_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        
        if project_crs != wgs84_crs:
            transform = QgsCoordinateTransform(
                project_crs, wgs84_crs, QgsProject.instance()
            )
            center = transform.transform(center)
        
        # Update inputs
        self.lat_input.setValue(center.y())
        self.lon_input.setValue(center.x())
        
        self.addr_result.setText(f"Map center: {center.y():.6f}, {center.x():.6f}")
        self.addr_result.setStyleSheet("color: #666; font-style: italic;")
