def add_name_field(data_list, id_field='company_id'):
    """
    Bổ sung trường *_name cho mỗi dict trong data_list dựa vào id_field dạng [id, name].
    Nếu không có hoặc lỗi, gán False.
    id_field: tên trường id (vd: company_id, department_id, ...)
    name_field sẽ tự động là id_field thay '_id' cuối cùng bằng '_name'.
    """
    if not id_field.endswith('_id'):
        raise ValueError('id_field phải kết thúc bằng _id')
    name_field = id_field[:-3] + '_name'
    for item in data_list:
        try:
            name_value = item[id_field][1]
            item[name_field] = name_value
        except Exception:
            item[name_field] = False
    return data_list
