# -*- coding: utf-8 -*-
import xmlrpc.client

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
