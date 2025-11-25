from PyQt5.QtWidgets import QDialog

from .export import get_json
from .libcoveofds.python_validate import PythonValidate
from .ui.validate import Ui_Dialog


def error_to_human_message(data):
    if data["type"] == "node_not_used_in_any_spans":
        return "A node is not used in any spans! The node's id is {}".format(
            data["node_id"]
        )
    if data["type"] == "span_start_node_not_found":
        return "A span's start node could not be found. The span's id is {} and the node id we can't find is {}".format(
            data["span_id"], data["missing_node_id"]
        )
    if data["type"] == "span_end_node_not_found":
        return "A span's end node could not be found. The span's id is {} and the node id we can't find is {}".format(
            data["span_id"], data["missing_node_id"]
        )


class ValidateDialog(QDialog):

    ui: Ui_Dialog

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def validate(self, layers, message_bar):
        data = get_json(layers)
        validator = PythonValidate()
        results = validator.validate(data)
        if not results:
            message_bar.pushMessage("No errors found while validating OFDS data!")
            return
        out = "\n".join(["ERROR: " + error_to_human_message(r) for r in results])
        self.ui.textBrowser.setText(out)
        self.show()
