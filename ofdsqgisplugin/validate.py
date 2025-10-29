from .export import get_json
from .libcoveofds.python_validate import PythonValidate


def validate(layers, message_bar):
    data = get_json(layers)
    validator = PythonValidate()
    results = validator.validate(data)
    if results:
        message_bar.pushMessage("ERROR: " + str(results[0]))
    else:
        message_bar.pushMessage("No errors found!")
