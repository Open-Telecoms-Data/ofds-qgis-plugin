from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QHBoxLayout, QLineEdit, QListView, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)
from qgis.core import QgsFeature, QgsJsonUtils

from ..lib import find_layers


class NetworkEditDialog(QMainWindow):

    def __init__(self):
        super().__init__()

        # window setup
        self.resize(600, 600)

        # central widget is vertical list
        central = QWidget()
        layout = QVBoxLayout(central)

        # First item is the form

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Network Name")

        layout.addWidget(self.name_field)

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
        self.setWindowTitle("EditOFDS Network")
        self.existing_data = data
        self.name_field.setText(data["name"])
        self.show()

    def save(self):
        self.layer.startEditing()

        if self.existing_data:
            for feature in self.layer.getFeatures():
                if feature.attribute("id") == self.existing_data["id"]:
                    break
            # TODO error if not found
        else:
            feature = QgsFeature(self.layer.fields())

        feature.setAttribute("name", self.name_field.displayText())

        if self.existing_data:
            if not self.layer.updateFeature(feature):
                raise Exception("Could not Update")
        else:
            if not self.layer.addFeature(feature):
                raise Exception("Could not add to table_name layer")

        if not self.layer.commitChanges():
            raise Exception("Could not commit layer")

        # TODO call refresh on the list of networks on home dialog
        self.hide()
