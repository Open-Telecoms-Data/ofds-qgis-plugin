"""
About Dialog for OFDS QGIS Plugin.

Shows plugin version, OFDS standard information, and links to resources.
"""

import os

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QPixmap, QDesktopServices, QFont

PLUGIN_DIR = os.path.dirname(__file__)


class AboutDialog(QDialog):
    """About dialog showing plugin and OFDS information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About OFDS QGIS Plugin")
        self.setFixedSize(480, 520)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(PLUGIN_DIR, "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Title
        title = QLabel("OFDS QGIS Plugin")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0078D7;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Open Fibre Data Standard")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(subtitle)
        
        # Version info box
        version_frame = QFrame()
        version_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #DDD;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        version_layout = QVBoxLayout(version_frame)
        version_layout.setSpacing(5)
        
        plugin_version = QLabel("<b>Plugin Version:</b> 1.0.0")
        plugin_version.setAlignment(Qt.AlignCenter)
        version_layout.addWidget(plugin_version)
        
        standard_version = QLabel("<b>OFDS Standard Version:</b> 0.3.0")
        standard_version.setAlignment(Qt.AlignCenter)
        version_layout.addWidget(standard_version)
        
        layout.addWidget(version_frame)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Description
        desc = QLabel(
            "<p>A QGIS plugin for working with the <b>Open Fibre Data Standard (OFDS)</b>.</p>"
            "<p>OFDS is a standard for publishing and sharing data on fibre optic "
            "telecommunication infrastructure, enabling consistent data exchange "
            "between organizations.</p>"
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # Links section
        links_label = QLabel("<b>Resources:</b>")
        links_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(links_label)
        
        # OFDS Website button
        website_btn = QPushButton("🌐  OFDS Website")
        website_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 12px;
            }
        """)
        website_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://open-fibre-data-standard.readthedocs.io/")
            )
        )
        layout.addWidget(website_btn)
        
        # GitHub button
        github_btn = QPushButton("📦  GitHub Repository")
        github_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 12px;
            }
        """)
        github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/Open-Telecoms-Data/ofds-qgis-plugin")
            )
        )
        layout.addWidget(github_btn)
        
        # Documentation button
        docs_btn = QPushButton("📖  Documentation")
        docs_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 12px;
            }
        """)
        docs_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://open-fibre-data-standard.readthedocs.io/en/latest/")
            )
        )
        layout.addWidget(docs_btn)
        
        # Spacer
        layout.addStretch()
        
        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)
        
        # Credits
        credits = QLabel(
            "<small>Developed by <b>Open Data Services Co-operative</b><br>"
            "Licensed under MIT License</small>"
        )
        credits.setAlignment(Qt.AlignCenter)
        credits.setStyleSheet("color: #666;")
        layout.addWidget(credits)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                font-size: 12px;
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        close_layout.addStretch()
        layout.addLayout(close_layout)
