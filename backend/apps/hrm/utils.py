import xmlrpc.client

ODOO_URL = "https://solienlacdientu.info"  # Thay đổi nếu cần
ODOO_DB = "goldsun"            # Thay đổi nếu cần
ODOO_USERNAME = "admin"             # Thay đổi nếu cần
ODOO_PASSWORD = "admin"  # Thay đổi nếu cần
ODOO_UID = 2  # Thay đổi nếu cần, UID của người dùng admin thường là 2
class OdooHRMService:
    def __init__(self, url=ODOO_URL, db=ODOO_DB, username=ODOO_USERNAME, password=ODOO_PASSWORD, uid=ODOO_UID):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = uid
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")


    def login(self, username, password):
        uid = self.common.authenticate(self.db, username, password, {})
        return uid

    def search_employees(self, domain=None, fields=None, batch_size=100):
        domain = domain or []
        fields = fields or ["id", "name", "work_email"]
        offset = 0
        all_results = []
        while True:
            results = self.models.execute_kw(
                self.db, self.uid, self.password,
                "hr.employee", "search_read",
                [domain], {"fields": fields, "limit": batch_size, "offset": offset}
            )
            if not results:
                break
            all_results.extend(results)
            offset += batch_size
        return all_results

    def create_employee(self, vals):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "hr.employee", "create",
            [vals]
        )

    def update_employee(self, employee_id, vals):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "hr.employee", "write",
            [[employee_id], vals]
        )

    def delete_employee(self, employee_id):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "hr.employee", "unlink",
            [[employee_id]]
        )

# Ví dụ sử dụng:
service = OdooHRMService()
print(service.search_employees())
# new_id = service.create_employee({"name": "Nguyen Van A"})
# service.update_employee(new_id, {"work_email": "a@example.com"})
# service.delete_employee(new_id)
