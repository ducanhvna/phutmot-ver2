# odoo_client.py
import requests


class OdooClient:
    def __init__(self, base_url, db):
        self.base_url = base_url
        self.db = db

    def authenticate(self, username, password):
        url = f"{self.base_url}/auth/token"
        payload = {
            'username': username,
            'password': password
        }
        response = requests.post(url, json=payload)
        return response.json()
