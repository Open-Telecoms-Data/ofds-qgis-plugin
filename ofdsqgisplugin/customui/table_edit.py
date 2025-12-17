from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QHBoxLayout,
                             QLabel, QLineEdit, QListView, QMainWindow,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)
from qgis.core import QgsFeature, QgsJsonUtils

from ..lib import find_layers
from .base import get_schema_information


class TableEditDialog(QMainWindow):

    def __init__(self, table_name):
        self.table_name = table_name
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
            get_schema_information()["tables"][table_name]["columns"]
        ):

            if field_info["name"] != "network_id":

                title = QLabel(field_info["title"], None)
                scroll_area_layout.addWidget(title)

                description = QLabel(field_info["description"], None)
                description.setWordWrap(True)
                scroll_area_layout.addWidget(description)

                if field_info["type"] == "text":
                    self.fields[field_idx] = QLineEdit()
                    scroll_area_layout.addWidget(self.fields[field_idx])

                elif field_info["type"] == "number":
                    self.fields[field_idx] = {
                        "select": QCheckBox(),
                        "number": QDoubleSpinBox(),
                    }
                    scroll_area_layout.addWidget(self.fields[field_idx]["select"])
                    scroll_area_layout.addWidget(self.fields[field_idx]["number"])

                elif field_info["type"] == "open_codelist":
                    self.fields[field_idx] = {"select": QComboBox()}
                    scroll_area_layout.addWidget(self.fields[field_idx]["select"])

                    # TODO must add a way for people to add new items

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
        self.network_data = None
        self.layers = find_layers()

    def discard(self):
        # TODO prompt user, are they sure?
        self.hide()

    def setup_form_options(self):
        """Sets up all the form options, like select entries.

        This is not done in __init__ for lifecycle reasons - __init__ may have been
        called a while ago and since then new data items might have been added to open codelists etc.
        So do it every time we start a new or an edit.
        """
        for field_idx, field_info in enumerate(
            get_schema_information()["tables"][self.table_name]["columns"]
        ):
            if field_info["type"] == "open_codelist":
                # clear current values
                self.fields[field_idx]["select"].clear()

                # load new values & add
                self.fields[field_idx]["values"] = []
                for codelist_feature in self.layers[
                    "codelist_open_" + field_info["codelist"][:-4]
                ].getFeatures():
                    self.fields[field_idx]["values"].append(
                        (
                            codelist_feature.attribute("id"),
                            codelist_feature.attribute("description"),
                        )
                    )
                self.fields[field_idx]["select"].addItems(
                    [""] + [i[1] for i in self.fields[field_idx]["values"]]
                )

    def start_new(self, network_data):
        if network_data:
            self.setWindowTitle(
                "New OFDS {} in network {}({})".format(
                    self.table_name, network_data["name"], network_data["ofds_id"]
                )
            )
        else:
            self.setWindowTitle("New OFDS " + self.table_name)
        self.network_data = network_data
        self.existing_data = None
        self.setup_form_options()
        self.show()

    def start_edit(self, data, network_data):

        # vars
        self.network_data = network_data
        self.existing_data = data

        # Sort out window
        self.setWindowTitle("EditOFDS " + self.table_name)
        self.setup_form_options()

        # Load data into fields
        for field_idx, field_info in enumerate(
            get_schema_information()["tables"][self.table_name]["columns"]
        ):
            if field_info["type"] == "text":
                if data[field_info["name"]]:
                    self.fields[field_idx].setText(data[field_info["name"]])
                else:
                    self.fields[field_idx].setText("")
            elif field_info["type"] == "number":
                if data[field_info["name"]]:
                    self.fields[field_idx]["select"].setChecked(True)
                    self.fields[field_idx]["number"].setValue(data[field_info["name"]])
                else:
                    self.fields[field_idx]["select"].setChecked(False)
                    self.fields[field_idx]["number"].setValue(0.0)
            elif field_info["type"] == "open_codelist":
                current_value = [
                    i[1]
                    for i in self.fields[field_idx]["values"]
                    if i[0] == data[field_info["name"]]
                ]
                if current_value:
                    self.fields[field_idx]["select"].setCurrentText(current_value[0])
                else:
                    self.fields[field_idx]["select"].setCurrentText("")

        # Show
        self.show()

    def save(self):
        # Start editing
        self.layers["networks"].startEditing()

        # Get feature, or make a new one
        if self.existing_data:
            for feature in self.layers[self.table_name].getFeatures():
                if feature.attribute("id") == self.existing_data["id"]:
                    break
            # TODO error if not found
        else:
            feature = QgsFeature(self.layers[self.table_name].fields())
            if self.network_data:
                feature.setAttribute("network_id", self.network_data["id"])

        # Set data

        for field_idx, field_info in enumerate(
            get_schema_information()["tables"][self.table_name]["columns"]
        ):
            if field_info["type"] == "text":
                feature.setAttribute(
                    field_info["name"], self.fields[field_idx].displayText()
                )

            elif field_info["type"] == "number":
                if self.fields[field_idx]["select"].isChecked():
                    feature.setAttribute(
                        field_info["name"], self.fields[field_idx]["number"].value()
                    )
                else:
                    feature.setAttribute(field_info["name"], None)

            elif field_info["type"] == "open_codelist":
                current_text = self.fields[field_idx]["select"].currentText()
                if current_text:
                    current_value = [
                        i[0]
                        for i in self.fields[field_idx]["values"]
                        if i[1] == current_text
                    ]
                    if current_value:
                        feature.setAttribute(field_info["name"], current_value[0])
                    else:
                        feature.setAttribute(field_info["name"], None)
                else:
                    feature.setAttribute(field_info["name"], None)

        # Update or add features
        if self.existing_data:
            if not self.layers[self.table_name].updateFeature(feature):
                raise Exception("Could not Update")
        else:
            if not self.layers[self.table_name].addFeature(feature):
                raise Exception("Could not add to table_name layer")

        # Commit
        if not self.layers[self.table_name].commitChanges():
            raise Exception("Could not commit layer")

        # TODO call refresh on the list of things in the last dialog

        # And hide the form
        self.hide()
