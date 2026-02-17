"""
Export to GeoPackage functionality for OFDS QGIS Plugin.

Exports all OFDS layers to a new GeoPackage file.
"""

import os

from qgis.core import (
    QgsVectorFileWriter, QgsProject, Qgis
)
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox


def export_to_geopackage(layers, iface):
    """Export all OFDS layers to a new GeoPackage file.
    
    Args:
        layers: dict of layer name -> QgsVectorLayer
        iface: QGIS interface
    """
    # Get save filename from user
    filename, _ = QFileDialog.getSaveFileName(
        None,
        "Save OFDS GeoPackage As",
        "",
        "GeoPackage (*.gpkg)"
    )
    
    if not filename:
        return  # User cancelled
    
    # Ensure .gpkg extension
    if not filename.lower().endswith('.gpkg'):
        filename += '.gpkg'
    
    # Check if file exists
    if os.path.exists(filename):
        reply = QMessageBox.question(
            None,
            "File Exists",
            f"'{os.path.basename(filename)}' already exists. Overwrite?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        # Remove existing file to start fresh
        try:
            os.remove(filename)
        except OSError as e:
            iface.messageBar().pushMessage(
                f"Error removing existing file: {e}",
                level=Qgis.Warning
            )
            return
    
    # Export each layer to the GeoPackage
    transform_context = QgsProject.instance().transformContext()
    
    # Define layer order - main tables first, then codelists
    layer_order = [
        'networks', 'nodes', 'spans', 'phases',
        'organisations', 'contracts',
        'nodes_internationalConnections', 'contracts_documents'
    ]
    
    # Add codelist tables
    codelist_tables = [
        'codelist_open_language', 
        'codelist_open_nodeType',
        'codelist_open_nodeTechnologies', 
        'codelist_open_spanTechnologies',
        'codelist_open_organisationRole', 
        'codelist_open_contractType',
        'codelist_open_mediaType', 
        'codelist_open_organisationIdentifierScheme'
    ]
    layer_order.extend(codelist_tables)
    
    first_layer = True
    exported_count = 0
    errors = []
    
    for layer_name in layer_order:
        if layer_name not in layers:
            continue
        
        layer = layers[layer_name]
        
        # Set up writer options
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = layer_name
        
        if first_layer:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
            first_layer = False
        else:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        
        # Write the layer
        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            filename,
            transform_context,
            options
        )
        
        if error[0] == QgsVectorFileWriter.NoError:
            exported_count += 1
        else:
            errors.append(f"{layer_name}: {error[1]}")
    
    # Show results
    if errors:
        for err in errors:
            iface.messageBar().pushMessage(
                f"Export error - {err}",
                level=Qgis.Warning,
                duration=5
            )
    
    if exported_count > 0:
        iface.messageBar().pushMessage(
            f"Successfully exported {exported_count} layers to {os.path.basename(filename)}",
            level=Qgis.Success,
            duration=5
        )
    else:
        iface.messageBar().pushMessage(
            "No layers were exported",
            level=Qgis.Warning,
            duration=5
        )
