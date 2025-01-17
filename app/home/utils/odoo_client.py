import xmlrpc.client


class OdooClient:
    def __init__(self, base_url, db):
        self.base_url = base_url
        self.db = db
        self.common = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/common")
        self.uid = None

    def authenticate(self, username, password):
        try:
            self.uid = self.common.authenticate(self.db, username, password, {})
            if self.uid:
                return {'status': 'success', 'user_id': self.uid}
            else:
                return {'status': 'fail', 'message': 'Invalid credentials'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
