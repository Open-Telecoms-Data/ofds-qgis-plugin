from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from .export import get_json
from .libcoveofds.python_validate import PythonValidate
from .ui.validate import Ui_Dialog


class ValidateDialog(QDialog):

    ui: Ui_Dialog

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.scrollAreaWidgetContents.setLayout(
            QVBoxLayout(self.ui.scrollAreaWidgetContents)
        )

    def validate(self, layers, message_bar):
        # Validate!
        data = get_json(layers)
        validator = PythonValidate()
        results = validator.validate(data)

        # If no errors, happy!
        if not results:
            message_bar.pushMessage("No errors found while validating OFDS data!")
            return

        # Clear all existing widgets
        layout = self.ui.scrollAreaWidgetContents.layout()
        for widget_no in range(0, layout.count()):
            if layout.itemAt(widget_no) != None:
                layout.itemAt(widget_no).widget().deleteLater()

        # Add new widgets
        for result in results:
            item = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel(str(result)))
            item.setLayout(layout)
            self.ui.scrollAreaWidgetContents.layout().addWidget(item)

        self.show()
