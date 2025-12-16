from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QListView, QListWidget,
                             QListWidgetItem, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from ..lib import find_layers
from .network_edit import NetworkEditDialog


class TableListDialog(QMainWindow):

    def __init__(self, table_name):
        self.table_name = table_name
        super().__init__()

        # window setup
        self.setWindowTitle("OFDS " + table_name)  # TODO better title
        self.resize(600, 600)

        # central widget is vertical list
        central = QWidget()
        layout = QVBoxLayout(central)

        # First item is a list view
        self.listview = QListWidget()
        layout.addWidget(self.listview)

        # Second item is butons
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.button_close_clicked)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Finally add central widget
        self.setCentralWidget(central)

        # Vars to track things
        self.network_data = {}

    def button_close_clicked(self):
        self.hide()

    def start(self, network_data):
        self.network_data = network_data
        self.load_data()
        self.show()

    def load_data(self):
        self.listview.clear()
        layers = find_layers()
        for f in layers[self.table_name].getFeatures():
            data = {}
            for field_name in layers[self.table_name].fields().names():
                data[field_name] = f.attribute(field_name)

            if data["network_id"] == self.network_data["id"]:

                row_widget = self._get_widget_for_phase(data)
                item = QListWidgetItem(self.listview)
                item.setSizeHint(row_widget.sizeHint())
                self.listview.addItem(item)
                self.listview.setItemWidget(item, row_widget)

    def _get_widget_for_phase(self, data):
        network_row_widget = QWidget()
        h = QHBoxLayout(network_row_widget)

        text_layout = QVBoxLayout()
        title = QLabel(str(data["ofds_id"]), None)
        subtitle = QLabel(str(data["name"] if "name" in data else data["title"]), None)
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        h.addLayout(text_layout)

        return network_row_widget
