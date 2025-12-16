from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QListView,
                             QMainWindow, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)
from qgis.core import QgsFeature, QgsJsonUtils

from ..lib import find_layers
from .base import get_schema_information


class NetworkEditDialog(QMainWindow):

    def __init__(self):
        super().__init__()

        # window setup
        self.resize(600, 600)

        # central widget is vertical list
        central = QWidget()
        layout = QVBoxLayout(central)

        # First item is the form
        self.fields = {}

        scroll_area = QScrollArea()
        scroll_area_widget = QWidget()
        scroll_area_layout = QVBoxLayout()
        scroll_area_widget.setLayout(scroll_area_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_area_widget)

        for field_idx, field_info in enumerate(
            get_schema_information()["tables"]["networks"]["columns"]
        ):
            if field_info["type"] == "text":
                title = QLabel(field_info["title"], None)
                scroll_area_layout.addWidget(title)

                description = QLabel(field_info["description"], None)
                description.setWordWrap(True)
                scroll_area_layout.addWidget(description)

                self.fields[field_idx] = QLineEdit()
                scroll_area_layout.addWidget(self.fields[field_idx])

        layout.addWidget(scroll_area)

        # Second item is butons
        btn_layout = QHBoxLayout()

        discard_btn = QPushButton("Discard")
        discard_btn.clicked.connect(self.discard)
        btn_layout.addWidget(discard_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        # Finally add central widget
        self.setCentralWidget(central)

        # Vars to track things
        self.existing_data = None
        self.layer = find_layers()["networks"]

    def discard(self):
        # TODO prompt user, are they sure?
        self.hide()

    def start_new(self):
        self.setWindowTitle("New OFDS Network")
        self.existing_data = None
        self.show()

    def start_edit(self, data):
        # Sort out window
        self.setWindowTitle("EditOFDS Network")
        self.existing_data = data

        # Load data into fields
        for field_idx, field_info in enumerate(
            get_schema_information()["tables"]["networks"]["columns"]
        ):
            if field_info["type"] == "text":
                if data[field_info["name"]]:
                    self.fields[field_idx].setText(data[field_info["name"]])
                else:
                    self.fields[field_idx].setText("")
        # Show
        self.show()

    def save(self):
        # Start editing
        self.layer.startEditing()

        # Get feature, or make a new one
        if self.existing_data:
            for feature in self.layer.getFeatures():
                if feature.attribute("id") == self.existing_data["id"]:
                    break
            # TODO error if not found
        else:
            feature = QgsFeature(self.layer.fields())

        # Set data

        for field_idx, field_info in enumerate(
            get_schema_information()["tables"]["networks"]["columns"]
        ):
            if field_info["type"] == "text":
                feature.setAttribute(
                    field_info["name"], self.fields[field_idx].displayText()
                )

        # Update or add features
        if self.existing_data:
            if not self.layer.updateFeature(feature):
                raise Exception("Could not Update")
        else:
            if not self.layer.addFeature(feature):
                raise Exception("Could not add to table_name layer")

        # Commit
        if not self.layer.commitChanges():
            raise Exception("Could not commit layer")

        # TODO call refresh on the list of networks on home dialog

        # And hide the form
        self.hide()
