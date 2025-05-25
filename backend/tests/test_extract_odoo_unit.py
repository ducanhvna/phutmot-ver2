import pytest
import xmlrpc.client
from app.utils import etl_odoo_to_minio

ODOO_BASE_URL = etl_odoo_to_minio.ODOO_BASE_URL
ODOO_DB = etl_odoo_to_minio.ODOO_DB
ODOO_USERNAME = etl_odoo_to_minio.ODOO_USERNAME
ODOO_PASSWORD = etl_odoo_to_minio.ODOO_PASSWORD

@pytest.fixture(scope="module")
def odoo_models():
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")
    return models, uid

def test_extract_employees(odoo_models):
    models, uid = odoo_models
    res = etl_odoo_to_minio.extract_employees(models, uid, 5)
    print("extract_employees:", res)
    assert isinstance(res, list)

def test_extract_contracts(odoo_models):
    models, uid = odoo_models
    res = etl_odoo_to_minio.extract_contracts(models, uid, 5)
    print("extract_contracts:", res)
    assert isinstance(res, list)

def test_extract_companies(odoo_models):
    models, uid = odoo_models
    res = etl_odoo_to_minio.extract_companies(models, uid, 5)
    print("extract_companies:", res)
    assert isinstance(res, list)

def test_extract_leaves(odoo_models):
    models, uid = odoo_models
    res = etl_odoo_to_minio.extract_leaves(models, uid, 5)
    print("extract_leaves:", res)
    assert isinstance(res, list)

def test_extract_attendance(odoo_models):
    models, uid = odoo_models
    res = etl_odoo_to_minio.extract_attendance(models, uid, 5)
    print("extract_attendance:", res)
    assert isinstance(res, list)

def test_common_authenticate_success():
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    print("common.authenticate uid:", uid)
    assert isinstance(uid, int) and uid > 0

def test_common_authenticate_fail_wrong_password():
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, "sai_password", {})
    print("common.authenticate (wrong password) uid:", uid)
    assert uid is False or uid == 0

def test_common_authenticate_fail_wrong_db():
    import pytest
    import xmlrpc.client
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    with pytest.raises(xmlrpc.client.Fault):
        common.authenticate("sai_db", ODOO_USERNAME, ODOO_PASSWORD, {})
