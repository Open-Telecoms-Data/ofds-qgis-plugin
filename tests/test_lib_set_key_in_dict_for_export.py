from ofdsqgisplugin.python.lib import get_deep_key_from_data_for_import


def test_1():
    assert "x" == get_deep_key_from_data_for_import({"key": "x"}, "key")


def test_2():
    assert "x" == get_deep_key_from_data_for_import({"key": {"key": "x"}}, "key/key")
