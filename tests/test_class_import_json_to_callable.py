from ofdsqgisplugin.python.import_from_json import ImportJSONToCallable


def test_get_deep_key_from_data_for_import_1():
    c = ImportJSONToCallable({}, lambda x: x, lambda x: x)
    assert "x" == c._get_deep_key_from_data_for_import({"key": "x"}, "key")


def test_get_deep_key_from_data_for_import_2():
    c = ImportJSONToCallable({}, lambda x: x, lambda x: x)
    assert "x" == c._get_deep_key_from_data_for_import({"key": {"key": "x"}}, "key/key")
