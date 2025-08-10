import xmlrpc.client

ODOO_URL = "https://solienlacdientu.info"  # Thay đổi nếu cần
ODOO_DB = "goldsun"            # Thay đổi nếu cần
ODOO_USERNAME = "admin"             # Thay đổi nếu cần
ODOO_PASSWORD = "admin"  # Thay đổi nếu cần

class OdooHRMService:
    def __init__(self, url=ODOO_URL, db=ODOO_DB, username=ODOO_USERNAME, password=ODOO_PASSWORD):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = 2
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        # self._login()

    def _login(self):
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})

    def search_employees(self, domain=None, fields=None, limit=10):
        domain = domain or []
        fields = fields or ["id", "name", "work_email"]
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "hr.employee", "search_read",
            [domain], {"fields": fields, "limit": limit}
        )

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
