# -*- coding: utf-8 -*-
import xmlrpc.client
import json

# Danh sách attribute mẫu cho sản phẩm trang sức
JEWELRY_ATTRIBUTES = [
    {
        "name": "Material",
        "type": "selection",
        "short_name": "MAT",
        "display_name": "Chất liệu",
        "required": True
    },
    {
        "name": "Color",
        "type": "selection",
        "short_name": "COL",
        "display_name": "Màu sắc",
        "required": True
    },
    {
        "name": "Weight",
        "type": "float",
        "short_name": "WGT",
        "display_name": "Trọng lượng (g)",
        "required": False
    },
    {
        "name": "Size",
        "type": "char",
        "short_name": "SIZ",
        "display_name": "Kích thước",
        "required": False
    },
    {
        "name": "Stone",
        "type": "selection",
        "short_name": "STN",
        "display_name": "Loại đá",
        "required": False
    }
]

JEWELRY_ATTRIBUTES_JSON = json.dumps(JEWELRY_ATTRIBUTES, ensure_ascii=False, indent=2)

def ensure_jewelry_attributes(url, db, username, password, product_id):
    """
    Kiểm tra product.template có đủ các attribute mẫu, nếu thiếu thì thêm vào.
    """
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    # Lấy các attribute line hiện có của product.template
    product = models.execute_kw(
        db, uid, password,
        'product.template', 'read',
        [[product_id]],
        {'fields': ['attribute_line_ids']}
    )
    if not product:
        return False
    product = product[0]
    existing_attr_line_ids = product.get('attribute_line_ids', [])
    # Lấy thông tin các attribute line
    existing_attr_lines = []
    if existing_attr_line_ids:
        existing_attr_lines = models.execute_kw(
            db, uid, password,
            'product.template.attribute.line', 'read',
            [existing_attr_line_ids],
            {'fields': ['attribute_id']}
        )
    # Lấy danh sách tên attribute đã có
    existing_attr_ids = [line['attribute_id'][0] for line in existing_attr_lines if line['attribute_id']]
    existing_attrs = []
    if existing_attr_ids:
        existing_attrs = models.execute_kw(
            db, uid, password,
            'product.attribute', 'read',
            [existing_attr_ids],
            {'fields': ['name']}
        )
    existing_attr_names = [attr['name'] for attr in existing_attrs]
    # Kiểm tra và thêm attribute nếu thiếu
    for attr in JEWELRY_ATTRIBUTES:
        if attr['name'] not in existing_attr_names:
            # Tìm hoặc tạo attribute
            attr_id = models.execute_kw(
                db, uid, password,
                'product.attribute', 'search',
                [[['name', '=', attr['name']]]]
            )
            if not attr_id:
                attr_id = models.execute_kw(
                    db, uid, password,
                    'product.attribute', 'create',
                    [{
                        'name': attr['name'],
                        'create_variant': 'no_variant',
                        # 'display_name': attr['display_name'],
                        # 'short_name': attr['short_name'],
                    }]
                )
            else:
                attr_id = attr_id[0]
            # Nếu là kiểu selection, float, char thì cần tạo value mặc định
            value_ids_list = []
            if attr['type'] in ['selection', 'float', 'char']:
                value_name = "Default"
                value_ids = models.execute_kw(
                    db, uid, password,
                    'product.attribute.value', 'search',
                    [[['name', '=', value_name], ['attribute_id', '=', attr_id]]]
                )
                if not value_ids:
                    value_id = models.execute_kw(
                        db, uid, password,
                        'product.attribute.value', 'create',
                        [{
                            'name': value_name,
                            'attribute_id': attr_id
                        }]
                    )
                else:
                    value_id = value_ids[0]
                value_ids_list = [value_id]
            # Thêm attribute line vào product.template
            models.execute_kw(
                db, uid, password,
                'product.template.attribute.line', 'create',
                [{
                    'product_tmpl_id': product_id,
                    'attribute_id': attr_id,
                    'value_ids': [(6, 0, value_ids_list)],
                }]
            )
    return True


def get_all_products(url, db, username, password, limit=10):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    offset = 0
    all_products = []
    while True:
        product_ids = models.execute_kw(
            db, uid, password,
            'product.template', 'search',
            [[]],
            {'limit': limit, 'offset': offset}
        )
        if not product_ids:
            break
        products = models.execute_kw(
            db, uid, password,
            'product.template', 'read',
            [product_ids],
            {'fields': ['id', 'name']}
        )
        all_products.extend(products)
        offset += limit
    return all_products


def get_product_detail(url, db, username, password, product_id):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    # Lấy chi tiết product.template
    product = models.execute_kw(
        db, uid, password,
        'product.template', 'read',
        [[product_id]],
        {'fields': ['id', 'name', 'attribute_line_ids']}
    )
    if not product:
        return None
    product = product[0]
    # Lấy chi tiết các attribute_line_ids
    attribute_lines = []
    if product.get('attribute_line_ids'):
        attribute_lines = models.execute_kw(
            db, uid, password,
            'product.template.attribute.line', 'read',
            [product['attribute_line_ids']],
            {'fields': ['id', 'attribute_id', 'value_ids']}
        )
        # Lấy thông tin value cho từng attribute line
        for line in attribute_lines:
            # Lấy tên attribute
            attribute = models.execute_kw(
                db, uid, password,
                'product.attribute', 'read',
                [ [line['attribute_id'][0]] ] if line['attribute_id'] else [],
                {'fields': ['name']}
            )
            line['attribute_name'] = attribute[0]['name'] if attribute else None
            # Lấy danh sách value
            values = []
            if line.get('value_ids'):
                values = models.execute_kw(
                    db, uid, password,
                    'product.attribute.value', 'read',
                    [line['value_ids']],
                    {'fields': ['name']}
                )
            line['values'] = [v['name'] for v in values]
    product['attribute_lines'] = attribute_lines
    return product


# Ví dụ gọi hàm
if __name__ == "__main__":
    url = "http://solienlacdientu.info"
    db = "goldsun"
    username = "admin"
    password = "admin"
    products = get_all_products(url, db, username, password, limit=10)
    print(products)

    product_id = 83  # Thay bằng id thực tế
    detail = get_product_detail(url, db, username, password, product_id)
    print(detail)
    ensure_jewelry_attributes(url, db, username, password, product_id)
