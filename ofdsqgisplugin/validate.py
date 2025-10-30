from PyQt5.QtWidgets import QDialog

from .export import get_json
from .libcoveofds.python_validate import PythonValidate
from .ui.validate import Ui_Dialog


class ValidateDialog(QDialog):

    ui: Ui_Dialog

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def validate(self, layers):
        data = get_json(layers)
        validator = PythonValidate()
        results = validator.validate(data)
        if results:
            out = "\n".join(["ERROR: " + str(r) for r in results])
        else:
            out = "No errors found!"
        self.ui.textBrowser.setText(out)
