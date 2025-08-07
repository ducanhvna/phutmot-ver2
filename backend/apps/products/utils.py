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

# Ví dụ gọi hàm
if __name__ == "__main__":
    url = "http://solienlacdientu.info"
    db = "goldsun"
    username = "admin"
    password = "admin"
    products = get_all_products(url, db, username, password, limit=10)
    print(products)
