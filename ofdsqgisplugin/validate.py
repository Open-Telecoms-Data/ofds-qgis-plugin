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
        return "A span's start node could not be found. The span's id is {} and the node id we can't find is {}.".format(
            data["span_id"], data["missing_node_id"]
        )
    if data["type"] == "span_end_node_not_found":
        return "A span's end node could not be found. The span's id is {} and the node id we can't find is {}.".format(
            data["span_id"], data["missing_node_id"]
        )
    if data["type"] == "node_phase_reference_id_not_found":
        return "A node's phase reference could not be found. The node's id is {} and the phase id we can't find is {}.".format(
            data["node_id"], data["phase_id_not_found"]
        )
    if data["type"] == "span_phase_reference_id_not_found":
        return "A span's phase reference could not be found. The span's id is {} and the phase id we can't find is {}.".format(
            data["span_id"], data["phase_id_not_found"]
        )
    if data["type"] == "node_organisation_reference_id_not_found":
        return "A node's organisation reference could not be found. The node's id is {} and the organisation id we can't find is {}.".format(
            data["node_id"], data["organisation_id_not_found"]
        )
    if data["type"] == "span_organisation_reference_id_not_found":
        return "A span's organisation reference could not be found. The span's id is {} and the organisation id we can't find is {}.".format(
            data["span_id"], data["organisation_id_not_found"]
        )
    if data["type"] == "duplicate_node_id":
        return "A node id is used more than once. The node id is {}.".format(
            data["node_id"]
        )
    if data["type"] == "duplicate_span_id":
        return "A span id is used more than once. The span id is {}.".format(
            data["span_id"]
        )
    if data["type"] == "duplicate_phase_id":
        return "A phase id is used more than once. The phase id is {}.".format(
            data["phase_id"]
        )
    if data["type"] == "duplicate_organisation_id":
        return "A organisation id is used more than once. The organisation id is {}.".format(
            data["organisation_id"]
        )
    if data["type"] == "duplicate_contract_id":
        return "A contract id is used more than once. The contract id is {}.".format(
            data["contract_id"]
        )
    return str(data)


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
