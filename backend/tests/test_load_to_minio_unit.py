import pytest
import pandas as pd
import os
from app.utils import etl_odoo_to_minio

class DummyMinio:
    def __init__(self):
        self.buckets = set()
        self.objects = {}
        self.policy = None
    def bucket_exists(self, b): return b in self.buckets
    def make_bucket(self, b): self.buckets.add(b)
    def get_bucket_policy(self, b): return self.policy or ''
    def set_bucket_policy(self, b, p): self.policy = p
    def fput_object(self, bucket, name, path): self.objects[name] = path

@pytest.fixture(autouse=True)
def patch_minio(monkeypatch):
    monkeypatch.setattr(etl_odoo_to_minio, 'Minio', lambda *a, **k: DummyMinio())
    yield

def test_bucket_created_if_not_exists():
    minio = DummyMinio()
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(etl_odoo_to_minio, 'Minio', lambda *a, **k: minio)
    data = {"apec_attendance_report": pd.DataFrame([{"company": "C1", "val": 1}])}
    etl_odoo_to_minio.MINIO_BUCKET = "test-bucket"
    etl_odoo_to_minio.load_to_minio(data)
    assert "test-bucket" in minio.buckets
    monkeypatch.undo()

def test_bucket_policy_set_if_not_public():
    minio = DummyMinio()
    minio.buckets.add("test-bucket")
    minio.policy = ''
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(etl_odoo_to_minio, 'Minio', lambda *a, **k: minio)
    data = {"apec_attendance_report": pd.DataFrame([{"company": "C1", "val": 1}])}
    etl_odoo_to_minio.MINIO_BUCKET = "test-bucket"
    etl_odoo_to_minio.load_to_minio(data)
    assert minio.policy is not None and 'Allow' in minio.policy
    monkeypatch.undo()

def test_no_file_exported_if_df_empty():
    data = {"apec_attendance_report": pd.DataFrame([])}
    links = etl_odoo_to_minio.load_to_minio(data)
    assert links == {}

def test_no_file_exported_if_no_company_col():
    df = pd.DataFrame([{"val": 1}])
    data = {"apec_attendance_report": df}
    links = etl_odoo_to_minio.load_to_minio(data)
    assert links == {}

def test_export_one_company(monkeypatch):
    called = {}
    def fake_export(data, outdir, data_key=None):
        called['ok'] = True
        # Tạo file giả
        fname = list(data.values())[0]["company"].iloc[0] + "__apec_attendance_report__2025-05-28.xlsx"
        with open(outdir + "/" + fname, "w") as f: f.write("x")
    monkeypatch.setitem(etl_odoo_to_minio.__dict__, 'export_sumary_attendance_report', fake_export)
    df = pd.DataFrame([{"company": "C1", "val": 1}])
    data = {"apec_attendance_report": df}
    links = etl_odoo_to_minio.load_to_minio(data, report_date="2025-05-28")
    assert called['ok']
    assert any("C1__apec_attendance_report__2025-05-28.xlsx" in k for k in links)

def test_export_many_companies(monkeypatch):
    called = set()
    def fake_export(data, outdir, data_key=None):
        company = list(data.values())[0]["company"].iloc[0]
        called.add(company)
        fname = company + "__apec_attendance_report__2025-05-28.xlsx"
        with open(outdir + "/" + fname, "w") as f: f.write("x")
    monkeypatch.setitem(etl_odoo_to_minio.__dict__, 'export_sumary_attendance_report', fake_export)
    df = pd.DataFrame([{"company": "C1", "val": 1}, {"company": "C2", "val": 2}])
    data = {"apec_attendance_report": df}
    links = etl_odoo_to_minio.load_to_minio(data, report_date="2025-05-28")
    assert called == {"C1", "C2"}
    assert all(f"{c}__apec_attendance_report__2025-05-28.xlsx" in links for c in ["C1", "C2"])

def test_export_func_with_and_without_data_key(monkeypatch):
    called = {}
    def fake_export_with_key(data, outdir, data_key=None):
        called['with'] = True
        fname = list(data.values())[0]["company"].iloc[0] + "__apec_attendance_report__2025-05-28.xlsx"
        with open(outdir + "/" + fname, "w") as f: f.write("x")
    def fake_export_no_key(data, outdir):
        called['no'] = True
        fname = list(data.values())[0]["company"].iloc[0] + "__feed_report__2025-05-28.xlsx"
        with open(outdir + "/" + fname, "w") as f: f.write("x")
    monkeypatch.setitem(etl_odoo_to_minio.__dict__, 'export_sumary_attendance_report', fake_export_with_key)
    monkeypatch.setitem(etl_odoo_to_minio.__dict__, 'export_feed_report', fake_export_no_key)
    df1 = pd.DataFrame([{"company": "C1", "val": 1}])
    df2 = pd.DataFrame([{"company": "C1", "val": 2}])
    data = {"apec_attendance_report": df1, "feed_report": df2}
    links = etl_odoo_to_minio.load_to_minio(data, report_date="2025-05-28")
    assert called['with']
    assert called['no']
    assert any("C1__apec_attendance_report__2025-05-28.xlsx" in k for k in links)
    assert any("C1__feed_report__2025-05-28.xlsx" in k for k in links)

def test_file_rename_and_upload(monkeypatch, tmp_path):
    # Kiểm tra file được rename đúng và upload đúng tên
    called = {}
    def fake_export(data, outdir, data_key=None):
        fname = list(data.values())[0]["company"].iloc[0] + "__apec_attendance_report__2025-05-28.xlsx"
        with open(tmp_path / fname, "w") as f: f.write("x")
    monkeypatch.setitem(etl_odoo_to_minio.__dict__, 'export_sumary_attendance_report', fake_export)
    df = pd.DataFrame([{"company": "C1", "val": 1}])
    data = {"apec_attendance_report": df}
    # Patch Minio để kiểm tra upload
    class DummyMinioUpload(DummyMinio):
        def fput_object(self, bucket, name, path):
            called['uploaded'] = (bucket, name, path)
    monkeypatch.setattr(etl_odoo_to_minio, 'Minio', lambda *a, **k: DummyMinioUpload())
    etl_odoo_to_minio.MINIO_BUCKET = "test-bucket"
    links = etl_odoo_to_minio.load_to_minio(data, report_date="2025-05-28")
    assert called['uploaded'][1] == "C1__apec_attendance_report__2025-05-28.xlsx"
    assert os.path.exists(called['uploaded'][2])
