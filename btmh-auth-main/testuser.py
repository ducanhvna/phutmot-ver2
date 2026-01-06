import xmlrpc.client

def odoo_login(url, db, username, password):
    """
    Hàm đăng nhập Odoo qua XML-RPC và trả về uid.
    
    :param url: URL server Odoo, ví dụ 'http://localhost:8069'
    :param db: Tên database Odoo
    :param username: Tài khoản đăng nhập
    :param password: Mật khẩu đăng nhập
    :return: uid (int) nếu đăng nhập thành công, None nếu thất bại
    """
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    try:
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"Đăng nhập thành công, uid = {uid}")
            return uid
        else:
            print("Đăng nhập thất bại")
            return None
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return None

import xmlrpc.client

def find_demo_user(username, url, db, uid, password):
    """
    Tìm user có login = 'demo' trong res.users
    """
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    try:
        users = models.execute_kw(
            db, uid, password,
            'res.users', 'search_read',
            [[['login', '=', username]]],
            {'fields': ['id', 'name', 'login'], 'limit': 1}
        )
        if users:
            print("Tìm thấy user:", users[0])
            return users[0]
        else:
            print(f"Không tìm thấy user {username}")
            return None
    except Exception as e:
        print(f"Lỗi truy vấn: {e}")
        return None



# Ví dụ sử dụng:
if __name__ == "__main__":
    url = "https://btmherp.baotinmanhhai.vn"
    db = "btmh_erp"
    username = "adminbtmh"
    password = "Btmh@2025#!"
    
    uid = odoo_login(url, db, username, password)
    if uid:
        demo_user = find_demo_user("nvbotchngoquyen@btmh.vn", url, db, uid, password)
