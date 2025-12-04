from ofdsqgisplugin.python.lib import set_key_in_dict_for_export


def test_1():
    data = {}
    set_key_in_dict_for_export(data, "key", "x")
    assert {"key": "x"} == data


def test_2():
    data = {}
    set_key_in_dict_for_export(data, "key/key", "x")
    assert {"key": {"key": "x"}} == data
