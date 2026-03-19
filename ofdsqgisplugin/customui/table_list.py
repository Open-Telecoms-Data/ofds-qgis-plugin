from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..lib import find_layers
from .table_edit import TableEditDialog


class TableListDialog(QMainWindow):

    def __init__(self, table_name):
        self.table_name = table_name
        super().__init__()

        # window setup
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

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new)
        btn_layout.addWidget(new_btn)

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
        self.setWindowTitle(
            "OFDS {} in network {}({})".format(
                self.table_name, network_data["name"], network_data["ofds_id"]
            )
        )
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

        button_layout = QVBoxLayout()

        button_edit = QPushButton("Edit")
        button_edit.clicked.connect(lambda: self.edit(data))
        button_layout.addWidget(button_edit)

        h.addLayout(button_layout)

        return network_row_widget

    def new(self):
        self.new_dialog = TableEditDialog(self.table_name)
        self.new_dialog.start_new(self.network_data)

    def edit(self, data):
        # TODO This means you can't open 2 edit dialogs at once, which you might want to do.
        self.edit_dialog = TableEditDialog(self.table_name)
        self.edit_dialog.start_edit(data, self.network_data)
