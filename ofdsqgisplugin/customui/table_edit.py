from qgis.core import QgsFeature, QgsJsonUtils
from qgis.PyQt.QtGui import QFont, QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..lib import find_layers
from .base import get_schema_information

INITIAL_WIDTH = 900
INITIAL_HEIGHT = 900


class TableEditDialog(QMainWindow):

    def __init__(self, table_name):
        self.table_name = table_name
        super().__init__()

        # window setup
        self.resize(INITIAL_WIDTH, INITIAL_HEIGHT)

        # central widget is vertical list
        central = QWidget()
        layout = QVBoxLayout(central)

        # First item is the form
        self.fields = {}
        self.relations = {}

        scroll_area = QScrollArea()
        scroll_area_widget = QWidget()
        scroll_area_layout = QVBoxLayout()
        scroll_area_widget.setLayout(scroll_area_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_area_widget)

        schema_information = get_schema_information()

        font_for_titles = QFont()
        font_for_titles.setBold(True)

        for field_idx, field_info in enumerate(
            schema_information["tables"][table_name]["columns"]
        ):

            if field_info["name"] != "network_id":

                title = QLabel(field_info["title"], None)
                title.setFont(font_for_titles)
                title.setStyleSheet("margin-top: 20px")
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

                    # TODO When select is off, number field should be disabled. Then it's clearer what select does.

                elif field_info["type"] == "open_codelist":
                    self.fields[field_idx] = {"select": QComboBox()}
                    scroll_area_layout.addWidget(self.fields[field_idx]["select"])

                    # TODO must add a way for people to add new items

                else:

                    scroll_area_layout.addWidget(QLabel("TODO", None))

        for relation_idx, relation_info in enumerate(
            schema_information["tables"][table_name]["relations"]
        ):

            title = QLabel(relation_info["title"], None)
            title.setFont(font_for_titles)
            title.setStyleSheet("margin-top: 20px")
            scroll_area_layout.addWidget(title)

            description = QLabel(relation_info["description"], None)
            description.setWordWrap(True)
            scroll_area_layout.addWidget(description)

            self.relations[relation_idx] = {
                "select": QComboBox(),
                "list": QListWidget(),
                "info": relation_info,
            }

            # setMaximumWidth is a bit hacky - but without it, these elements take up
            # a lot of horizontal area forcing a scroll and I'm not sure why
            self.relations[relation_idx]["list"].setMaximumWidth(INITIAL_WIDTH - 50)
            self.relations[relation_idx]["select"].setMaximumWidth(INITIAL_WIDTH - 50)

            scroll_area_layout.addWidget(self.relations[relation_idx]["list"])

            options_layout = QHBoxLayout()

            self.relations[relation_idx]["select"].setMaximumWidth(INITIAL_WIDTH - 150)
            options_layout.addWidget(self.relations[relation_idx]["select"])

            add_btn = QPushButton("Add")
            add_btn.clicked.connect(lambda y, x=relation_idx: self.add_relation_item(x))
            options_layout.addWidget(add_btn)

            scroll_area_layout.addLayout(options_layout)

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

        self.existing_data must be set correctly before calling this.
        """
        schema_information = get_schema_information()

        for field_idx, field_info in enumerate(
            schema_information["tables"][self.table_name]["columns"]
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

        for relation_idx, relation_info in enumerate(
            schema_information["tables"][self.table_name]["relations"]
        ):

            # clear current values
            self.relations[relation_idx]["select"].clear()
            self.relations[relation_idx]["list"].clear()

            # load new values & add
            self.relations[relation_idx]["values"] = []
            description_field = (
                "description" if relation_info.get("codelist") else "name"
            )
            for codelist_feature in self.layers[
                relation_info["related_table"]
            ].getFeatures():
                self.relations[relation_idx]["values"].append(
                    (
                        codelist_feature.attribute("id"),
                        codelist_feature.attribute(description_field),
                    )
                )
            self.relations[relation_idx]["select"].addItems(
                [i[1] for i in self.relations[relation_idx]["values"]]
            )

            # current values
            self.relations[relation_idx]["selected_values"] = (
                self.get_current_values_for_relationship(relation_idx)
            )

            # Put current values in UI
            for value in self.relations[relation_idx]["selected_values"]:
                self._add_relation_item_to_list(
                    relation_idx,
                    value,
                    [
                        i[1]
                        for i in self.relations[relation_idx]["values"]
                        if i[0] == value
                    ][0],
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

    def get_current_values_for_relationship(self, relation_idx):

        if not self.existing_data:
            return []

        out = []

        for feature in self.layers[
            self.relations[relation_idx]["info"]["mapping_table"]
        ].getFeatures():
            if feature.attribute("base_id") == self.existing_data["id"]:
                out.append(feature.attribute("related_id"))

        return out

    def add_relation_item(self, relation_idx):
        current_text = self.relations[relation_idx]["select"].currentText()
        current_value = [
            i for i in self.relations[relation_idx]["values"] if i[1] == current_text
        ]
        current_value_id, current_value_label = current_value[0]

        if current_value_id not in self.relations[relation_idx]["selected_values"]:
            # store in state, ready for saving
            self.relations[relation_idx]["selected_values"].append(current_value_id)
            # write into UI
            self._add_relation_item_to_list(
                relation_idx, current_value_id, current_value_label
            )

    def _add_relation_item_to_list(self, relation_idx, value_id, value_label):
        row_widget = QWidget()
        h = QHBoxLayout(row_widget)

        text_layout = QVBoxLayout()
        title = QLabel(str(value_label), None)
        title.setWordWrap(True)
        text_layout.addWidget(title)
        h.addLayout(text_layout)

        button_layout = QVBoxLayout()

        button_remove = QPushButton("Remove (TODO)")
        button_layout.addWidget(button_remove)

        h.addLayout(button_layout)

        item = QListWidgetItem(self.relations[relation_idx]["list"])
        item.setSizeHint(row_widget.sizeHint())
        self.relations[relation_idx]["list"].addItem(item)
        self.relations[relation_idx]["list"].setItemWidget(item, row_widget)

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
        schema_information = get_schema_information()

        for field_idx, field_info in enumerate(
            schema_information["tables"][self.table_name]["columns"]
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

        # Update or add main feature
        if self.existing_data:
            if not self.layers[self.table_name].updateFeature(feature):
                raise Exception("Could not Update")
        else:
            if not self.layers[self.table_name].addFeature(feature):
                raise Exception("Could not add to table_name layer")

        # Commit
        if not self.layers[self.table_name].commitChanges():
            raise Exception("Could not commit layer")

        # Now relations
        # (For new items, we need to make sure we have an database id saved before we do this)
        for relation_idx, relation_info in enumerate(
            schema_information["tables"][self.table_name]["relations"]
        ):

            # Get current options in DB
            current_options = self.get_current_values_for_relationship(relation_idx)

            # Work out which ones we need to delete or add
            delete_ids = [
                i
                for i in current_options
                if i not in self.relations[relation_idx]["selected_values"]
            ]
            add_ids = [
                i
                for i in self.relations[relation_idx]["selected_values"]
                if i not in current_options
            ]

            if delete_ids or add_ids:
                # start editing
                self.layers[relation_info["mapping_table"]].startEditing()

                # Delete ones!
                # TODO

                # Add ones!
                for add_id in add_ids:
                    relation_feature = QgsFeature(
                        self.layers[relation_info["mapping_table"]].fields()
                    )
                    relation_feature.setAttribute("base_id", feature.attribute("id"))
                    relation_feature.setAttribute("related_id", add_id)
                    if not self.layers[relation_info["mapping_table"]].addFeature(
                        relation_feature
                    ):
                        raise Exception(
                            "Could not add to {} layer".format(
                                relation_info["mapping_table"]
                            )
                        )

                # And commit
                if not self.layers[relation_info["mapping_table"]].commitChanges():
                    raise Exception(
                        "Could not commit {} layer".format(
                            relation_info["mapping_table"]
                        )
                    )

        # TODO call refresh on the list of things in the last dialog

        # And hide the form
        self.hide()
