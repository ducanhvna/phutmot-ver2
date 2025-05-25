import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.hrms.employee import EmployeeLogin, Employee, EmployeeContract, EmployeeAttendance, EmployeeShift, EmployeeProject
from app.db import SessionLocal

client = TestClient(app)

def setup_buyer_full():
    db = SessionLocal()
    db.query(EmployeeLogin).delete()
    db.query(Employee).delete()
    db.query(EmployeeContract).delete()
    db.query(EmployeeAttendance).delete()
    db.query(EmployeeShift).delete()
    db.query(EmployeeProject).delete()
    db.add(Employee(employee_code="B001", company_id=1, info={"name": "Test User"}, created_by="test"))
    db.add(EmployeeLogin(employee_code="B001", company_id=1, info={"password": "123456"}, created_by="test"))
    db.add(EmployeeContract(employee_code="B001", company_id=1, month=5, year=2025, info={"contract": "HĐLĐ"}, created_by="test"))
    db.add(EmployeeAttendance(employee_code="B001", company_id=1, month=5, year=2025, info={"days": 20}, created_by="test"))
    db.add(EmployeeShift(employee_code="B001", company_id=1, month=5, year=2025, info={"shift": "Sáng"}, created_by="test"))
    db.add(EmployeeProject(employee_code="B001", company_id=1, month=5, year=2025, info={"project": "Dự án A"}, created_by="test"))
    db.commit()
    db.close()

@pytest.mark.usefixtures("setup_test_db")
def test_employee_info_001():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    assert resp.status_code == 200

def test_employee_info_002():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee/info", headers=headers)
    assert r.status_code == 200

def test_employee_info_003():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee/info", headers=headers)
    assert r.json()["name"] == "Test User"

def test_employee_info_004():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-login/info/noauth", headers=headers)
    assert r.status_code == 200

def test_employee_info_005():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-login/info/noauth", headers=headers)
    assert r.json()["password"] == "123456"

def test_employee_info_006():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-contract/info?month=5&year=2025", headers=headers)
    assert r.status_code == 200

def test_employee_info_007():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-contract/info?month=5&year=2025", headers=headers)
    assert r.json()["contract"] == "HĐLĐ"

def test_employee_info_008():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-attendance/info?month=5&year=2025", headers=headers)
    assert r.status_code == 200

def test_employee_info_009():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-attendance/info?month=5&year=2025", headers=headers)
    assert r.json()["days"] == 20

def test_employee_info_010():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-shift/info?month=5&year=2025", headers=headers)
    assert r.status_code == 200

def test_employee_info_011():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-shift/info?month=5&year=2025", headers=headers)
    assert r.json()["shift"] == "Sáng"

def test_employee_info_012():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-project/info?month=5&year=2025", headers=headers)
    assert r.status_code == 200

def test_employee_info_013():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-project/info?month=5&year=2025", headers=headers)
    assert r.json()["project"] == "Dự án A"

# Các test case bất thường
@pytest.mark.usefixtures("setup_test_db")
def test_employee_info_abnormal_001():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "sai_pass"
    })
    assert resp.status_code == 401

def test_employee_info_abnormal_002():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B999", "company_id": 1, "password": "123456"
    })
    assert resp.status_code == 401

def test_employee_info_abnormal_003():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 99, "password": "123456"
    })
    assert resp.status_code == 401

def test_employee_info_abnormal_004():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    bad_headers = {"Authorization": "Bearer abc.def.ghi"}
    r = client.get("/api/hrms/employee/info", headers=bad_headers)
    assert r.status_code == 401

def test_employee_info_abnormal_005():
    setup_buyer_full()
    r = client.get("/api/hrms/employee/info")
    assert r.status_code == 422 or r.status_code == 401

def test_employee_info_abnormal_006():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/hrms/employee-contract/info?month=1&year=2024", headers=headers)
    assert r.status_code == 200
    assert r.json() is None
