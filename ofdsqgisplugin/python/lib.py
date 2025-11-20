def set_key_in_dict_for_export(data, key, value, type=""):
    if not value:
        return
    key_bits = key.split("/")
    final_key = key_bits.pop(-1)
    for key_bit in key_bits:
        if key_bit in data:
            data = data[key_bit]
        else:
            data[key_bit] = {}
            data = data[key_bit]
    if type == "boolean":
        data[final_key] = value == "true"
    elif type == "integer":
        data[final_key] = int(value)
    elif type == "number":
        data[final_key] = float(value)
    elif type == "foreignkey":
        data[final_key] = {"id": value}
    else:
        data[final_key] = value


def get_deep_key_from_data_for_import(data, key):
    key_bits = key.split("/")
    final_key = key_bits.pop(-1)
    for key_bit in key_bits:
        if key_bit in data and isinstance(data[key_bit], dict):
            data = data[key_bit]
        else:
            return None
    return data.get(final_key)
