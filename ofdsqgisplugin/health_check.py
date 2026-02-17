"""
Health Check Dialog for OFDS QGIS Plugin.

Provides duplicate detection for IDs and geometries in OFDS layers.
"""

import math

from qgis.PyQt.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QProgressBar,
    QGroupBox, QCheckBox
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor


class HealthCheckDialog(QDialog):
    """Dialog for running health checks on OFDS data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OFDS Health Check")
        self.resize(700, 500)
        self.layers = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Options group
        options_group = QGroupBox("Check Options")
        options_layout = QVBoxLayout()
        
        self.check_id_duplicates = QCheckBox("Check for duplicate IDs")
        self.check_id_duplicates.setChecked(True)
        options_layout.addWidget(self.check_id_duplicates)
        
        self.check_geom_duplicates = QCheckBox("Check for duplicate geometries")
        self.check_geom_duplicates.setChecked(True)
        options_layout.addWidget(self.check_geom_duplicates)
        
        self.check_near_duplicates = QCheckBox("Check for near-duplicate nodes (within ~1m)")
        self.check_near_duplicates.setChecked(False)
        options_layout.addWidget(self.check_near_duplicates)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)
        
        # Results label
        self.results_label = QLabel("Click 'Run Health Check' to start...")
        layout.addWidget(self.results_label)
        
        # Results list
        self.listwidget = QListWidget()
        self.listwidget.setWordWrap(True)
        self.listwidget.setAlternatingRowColors(True)
        layout.addWidget(self.listwidget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("Run Health Check")
        self.run_btn.clicked.connect(self._run_check)
        btn_layout.addWidget(self.run_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def start(self, layers):
        """Start the health check dialog with the given layers.
        
        Args:
            layers: dict of layer name -> QgsVectorLayer
        """
        self.layers = layers
        self.listwidget.clear()
        self.progress.setValue(0)
        self.results_label.setText("Click 'Run Health Check' to start...")
        self.show()
    
    def _run_check(self):
        """Run all enabled health checks."""
        if not self.layers:
            self.results_label.setText("Error: No layers available")
            return
        
        self.listwidget.clear()
        self.progress.setValue(0)
        self.run_btn.setEnabled(False)
        self.results_label.setText("Running checks...")
        
        issues = []
        total_checks = sum([
            self.check_id_duplicates.isChecked(),
            self.check_geom_duplicates.isChecked(),
            self.check_near_duplicates.isChecked()
        ])
        
        if total_checks == 0:
            self.results_label.setText("No checks selected")
            self.run_btn.setEnabled(True)
            return
        
        current_check = 0
        
        # Check for duplicate IDs
        if self.check_id_duplicates.isChecked():
            self.progress.setFormat("Checking duplicate IDs... %p%")
            issues.extend(self._check_id_duplicates())
            current_check += 1
            self.progress.setValue(int(current_check / total_checks * 100))
        
        # Check for duplicate geometries
        if self.check_geom_duplicates.isChecked():
            self.progress.setFormat("Checking duplicate geometries... %p%")
            issues.extend(self._check_geometry_duplicates())
            current_check += 1
            self.progress.setValue(int(current_check / total_checks * 100))
        
        # Check for near-duplicate nodes
        if self.check_near_duplicates.isChecked():
            self.progress.setFormat("Checking near-duplicate nodes... %p%")
            issues.extend(self._check_near_duplicate_nodes())
            current_check += 1
            self.progress.setValue(int(current_check / total_checks * 100))
        
        # Display results
        self.progress.setFormat("%p%")
        self.progress.setValue(100)
        
        if not issues:
            item = QListWidgetItem("✓ No issues found!")
            item.setForeground(QColor(0, 128, 0))  # Green
            self.listwidget.addItem(item)
            self.results_label.setText("Health check complete: No issues found!")
        else:
            for issue in issues:
                item = QListWidgetItem(issue)
                item.setForeground(QColor(200, 0, 0))  # Red
                self.listwidget.addItem(item)
            self.results_label.setText(f"Health check complete: {len(issues)} issue(s) found")
        
        self.run_btn.setEnabled(True)
    
    def _check_id_duplicates(self):
        """Check for duplicate OFDS IDs within each layer.
        
        Returns:
            list: List of issue description strings
        """
        issues = []
        
        # Layers to check for duplicate IDs
        layers_to_check = ['nodes', 'spans', 'networks', 'phases', 'organisations', 'contracts']
        
        for layer_name in layers_to_check:
            if layer_name not in self.layers:
                continue
            
            layer = self.layers[layer_name]
            seen_ids = {}
            
            for feature in layer.getFeatures():
                ofds_id = feature.attribute('ofds_id')
                if ofds_id and ofds_id != '':
                    if ofds_id in seen_ids:
                        issues.append(
                            f"⚠ Duplicate {layer_name} ID: '{ofds_id}' "
                            f"(feature IDs {seen_ids[ofds_id]} and {feature.id()})"
                        )
                    else:
                        seen_ids[ofds_id] = feature.id()
        
        return issues
    
    def _check_geometry_duplicates(self):
        """Check for features with identical geometries.
        
        Returns:
            list: List of issue description strings
        """
        issues = []
        
        # Only check geographic layers
        layers_to_check = ['nodes', 'spans']
        
        for layer_name in layers_to_check:
            if layer_name not in self.layers:
                continue
            
            layer = self.layers[layer_name]
            geometries = {}
            
            for feature in layer.getFeatures():
                geom = feature.geometry()
                if geom.isNull() or geom.isEmpty():
                    continue
                
                # Use WKT as geometry key (exact match with 8 decimal precision)
                wkt = geom.asWkt(precision=8)
                ofds_id = feature.attribute('ofds_id')
                if not ofds_id or ofds_id == '':
                    ofds_id = f"fid:{feature.id()}"
                
                if wkt in geometries:
                    issues.append(
                        f"⚠ Duplicate {layer_name} geometry: '{ofds_id}' "
                        f"has same location as '{geometries[wkt]}'"
                    )
                else:
                    geometries[wkt] = ofds_id
        
        return issues
    
    def _check_near_duplicate_nodes(self, tolerance=0.00001):
        """Check for nodes that are very close to each other.
        
        Args:
            tolerance: Distance threshold in map units (degrees for WGS84)
                      0.00001 degrees ≈ 1.1 meters at equator
        
        Returns:
            list: List of issue description strings
        """
        issues = []
        
        if 'nodes' not in self.layers:
            return issues
        
        nodes_layer = self.layers['nodes']
        nodes_data = []
        
        # Collect all node positions
        for feature in nodes_layer.getFeatures():
            geom = feature.geometry()
            if geom.isNull() or geom.isEmpty():
                continue
            
            point = geom.asPoint()
            ofds_id = feature.attribute('ofds_id')
            if not ofds_id or ofds_id == '':
                ofds_id = f"fid:{feature.id()}"
            
            nodes_data.append({
                'id': ofds_id,
                'x': point.x(),
                'y': point.y()
            })
        
        # Check distances between all pairs (O(n²) but necessary for this check)
        for i, node1 in enumerate(nodes_data):
            for node2 in nodes_data[i + 1:]:
                dist = math.sqrt(
                    (node2['x'] - node1['x'])**2 +
                    (node2['y'] - node1['y'])**2
                )
                # Near but not exactly the same (exact duplicates caught by geometry check)
                if dist < tolerance and dist > 0:
                    # Convert to approximate meters for display
                    dist_meters = dist * 111000  # Rough conversion at equator
                    issues.append(
                        f"⚠ Near-duplicate nodes: '{node1['id']}' and "
                        f"'{node2['id']}' are only ~{dist_meters:.1f}m apart"
                    )
        
        return issues
