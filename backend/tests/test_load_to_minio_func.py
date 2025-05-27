from app.utils import etl_odoo_to_minio
import pandas as pd

def test_load_to_minio(monkeypatch):
    # Patch Minio client
    class DummyMinio:
        def bucket_exists(self, b): return True
        def make_bucket(self, *a, **k): return None
        def get_bucket_policy(self, *a, **k): return '{"Effect":"Allow","Principal":"*"}'
        def set_bucket_policy(self, *a, **k): return None
        def fput_object(self, *a, **k): return None
        def list_objects(self, *a, **k): return []
    monkeypatch.setattr(etl_odoo_to_minio, 'Minio', lambda *a, **k: DummyMinio())
    df = pd.DataFrame([{"id": 1, "name": "Nguyen Van A"}])
    url = etl_odoo_to_minio.load_to_minio({"employees": df}, "test_report")
    assert isinstance(url, str)
    assert url.startswith("http://")
