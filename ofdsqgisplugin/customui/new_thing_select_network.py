from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QListView, QListWidget,
                             QListWidgetItem, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from ..lib import find_layers
from .table_edit import TableEditDialog


class NewThingSelectNetworkDialog(QMainWindow):

    def __init__(self, table_name, feature_id):
        self.table_name = table_name
        self.feature_id = feature_id
        super().__init__()

        # window setup
        self.setWindowTitle("Select Network")
        self.resize(600, 600)

        # central widget is vertical list
        central = QWidget()
        layout = QVBoxLayout(central)

        # First item is a list view
        self.listview = QListWidget()
        layout.addWidget(self.listview)

        # Second item is butons
        btn_layout = QHBoxLayout()

        close_btn = QPushButton("Cancel")
        close_btn.clicked.connect(self.button_close_clicked)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Finally add central widget
        self.setCentralWidget(central)

    def button_close_clicked(self):
        self.hide()

    def start(self):
        self.load_networks()
        self.show()

    def load_networks(self):
        self.listview.clear()
        layers = find_layers()
        for f in layers["networks"].getFeatures():
            data = {}
            for field_name in layers["networks"].fields().names():
                data[field_name] = f.attribute(field_name)

            row_widget = self._get_widget_for_network(data)
            item = QListWidgetItem(self.listview)
            item.setSizeHint(row_widget.sizeHint())
            self.listview.addItem(item)
            self.listview.setItemWidget(item, row_widget)

    def _get_widget_for_network(self, data):
        network_row_widget = QWidget()
        h = QHBoxLayout(network_row_widget)

        text_layout = QVBoxLayout()
        title = QLabel(str(data["ofds_id"]), None)
        subtitle = QLabel(str(data["name"]), None)
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        h.addLayout(text_layout)

        button_layout = QVBoxLayout()

        button_select = QPushButton("Select")
        button_select.clicked.connect(lambda: self.select(data))
        button_layout.addWidget(button_select)

        h.addLayout(button_layout)

        return network_row_widget

    def select(self, network_data):
        layers = find_layers()

        # Get feature
        feature = layers[self.table_name].getFeature(self.feature_id)

        # Set the network ID on this feature and save it
        feature.setAttribute("network_id", network_data["id"])
        layers[self.table_name].startEditing()
        if not layers[self.table_name].updateFeature(feature):
            raise Exception("Could not Update")
        if not layers[self.table_name].commitChanges():
            raise Exception("Could not commit layer")

        # Load data to pass on
        feature_data = {}
        for field_name in layers[self.table_name].fields().names():
            feature_data[field_name] = feature.attribute(field_name)

        # Open the dialog to edit more fields
        self.next_dialog = TableEditDialog(self.table_name)
        self.next_dialog.start_edit(feature_data, network_data)

        # Close this one
        self.close()
