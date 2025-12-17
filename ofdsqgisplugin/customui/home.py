from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QListView, QListWidget,
                             QListWidgetItem, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from ..lib import find_layers
from .table_edit import TableEditDialog
from .table_list import TableListDialog


class HomeDialog(QMainWindow):

    def __init__(self):
        super().__init__()

        # window setup
        self.setWindowTitle("OFDS Networks")
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
        refresh_btn.clicked.connect(self.load_networks)
        btn_layout.addWidget(refresh_btn)

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new)
        btn_layout.addWidget(new_btn)

        close_btn = QPushButton("Close")
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

        button_edit = QPushButton("Edit")
        button_edit.clicked.connect(lambda: self.edit(data))
        button_layout.addWidget(button_edit)

        button_table_1 = QPushButton("Nodes")
        button_table_1.clicked.connect(lambda: self.table_list("nodes", data))
        button_layout.addWidget(button_table_1)

        button_table_2 = QPushButton("Spans")
        button_table_2.clicked.connect(lambda: self.table_list("spans", data))
        button_layout.addWidget(button_table_2)

        button_table_3 = QPushButton("Phases")
        button_table_3.clicked.connect(lambda: self.table_list("phases", data))
        button_layout.addWidget(button_table_3)

        button_table_4 = QPushButton("Organisations")
        button_table_4.clicked.connect(lambda: self.table_list("organisations", data))
        button_layout.addWidget(button_table_4)

        button_table_5 = QPushButton("Contracts")
        button_table_5.clicked.connect(lambda: self.table_list("contracts", data))
        button_layout.addWidget(button_table_5)

        h.addLayout(button_layout)

        return network_row_widget

    def new(self):
        self.network_new = TableEditDialog("networks")
        self.network_new.start_new(None)

    def edit(self, data):
        # TODO This means you can't open 2 edit dialogs at once, which you might want to do.
        self.network_new = TableEditDialog("networks")
        self.network_new.start_edit(data, None)

    def table_list(self, table_name, data):
        self.table_list_dialog = TableListDialog(table_name)
        self.table_list_dialog.start(data)
