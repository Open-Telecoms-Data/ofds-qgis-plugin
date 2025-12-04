def set_key_in_dict_for_export(
    data, key, value, type="", open_codelist_ids_to_codes_mappings={}
):
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
    elif type == "foreign_key_id_name_dict":
        data[final_key] = {"id": value}
    elif type == "open_codelist" and value in open_codelist_ids_to_codes_mappings:
        data[final_key] = open_codelist_ids_to_codes_mappings[value]
    else:
        data[final_key] = value
