import xmlrpc.client
from django.conf import settings


class OdooXMLRPC:
    def __init__(self):
        self.url = settings.ERP_URL
        self.db = settings.ERP_DB
        self.username = settings.ERP_USERNAME
        self.password = settings.ERP_PASSWORD
        self.uid = self.authenticate()
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def authenticate(self):
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        return common.authenticate(self.db, self.username, self.password, {})

    def get_employees(self, offset=0, limit=10):
        employees = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            'hr.employee',
            'search_read',
            [[]],
            {'fields': ['id', 'name'], 'offset': offset, 'limit': limit}
        )
        return employees

    def get_total_records(self):
        total_records = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            'hr.employee',
            'search',
            [[]]
        )
        return len(total_records)
