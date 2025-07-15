import xmlrpc.client

REALATTENDANT_HOST = "https://admin.hinosoft.com"
DB_NAME = "odoo"
USERNAME = "admin"
PASSWORD = "admin"

# Đăng nhập Odoo, trả về uid và models object
def odoo_login(username=USERNAME, password=PASSWORD):
    common = xmlrpc.client.ServerProxy(f"{REALATTENDANT_HOST}/xmlrpc/2/common")
    uid = common.authenticate(DB_NAME, username, password, {})
    if not uid:
        raise Exception("Đăng nhập Odoo thất bại!")
    models = xmlrpc.client.ServerProxy(f"{REALATTENDANT_HOST}/xmlrpc/2/object")
    return uid, models

# Lấy danh sách fields và type của model mrp.workcenter.productivity
def get_model_fields(model_name="mrp.workcenter.productivity"):
    uid, models = odoo_login()
    fields = models.execute_kw(DB_NAME, uid, PASSWORD, model_name, 'fields_get', [], {'attributes': ['string', 'type', 'required', 'readonly']})
    print(f"\n--- Danh sách trường của model {model_name} ---")
    for field_name, field_info in fields.items():
        print(f"{field_name}: {field_info['string']} | type={field_info['type']} | required={field_info['required']} | readonly={field_info['readonly']}")
    print("\n--- Danh sách loss ---")
    loss_list = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'mrp.workcenter.productivity.loss', 'search_read',
        [{}, ['id', 'name', 'loss_type']]
    )
    for loss in loss_list:
        print(f"{loss['id']}: {loss['name']} (loss_type={loss['loss_type']})")

if __name__ == "__main__":
    get_model_fields()
