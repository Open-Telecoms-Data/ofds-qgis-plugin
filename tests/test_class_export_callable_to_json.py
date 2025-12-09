from ofdsqgisplugin.python.export_to_json import ExportCallableToJSON


def test_1():
    data = {}
    c = ExportCallableToJSON(lambda x: x)
    c._set_key_in_dict_for_export(data, "key", "x")
    assert {"key": "x"} == data


def test_2():
    data = {}
    c = ExportCallableToJSON(lambda x: x)
    c._set_key_in_dict_for_export(data, "key/key", "x")
    assert {"key": {"key": "x"}} == data
