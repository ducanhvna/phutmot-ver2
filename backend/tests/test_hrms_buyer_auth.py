import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.hrms.employee import EmployeeLogin, Employee, EmployeeContract, EmployeeAttendance, EmployeeShift, EmployeeProject
from app.db import SessionLocal

client = TestClient(app)

def setup_buyer():
    db = SessionLocal()
    db.query(EmployeeLogin).delete()
    db.add(EmployeeLogin(employee_code="B001", company_id=1, info={"password": "123456"}, created_by="test"))
    db.commit()
    db.close()

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
def test_employee_login_auth_001():
    setup_buyer()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    assert resp.status_code == 200

def test_employee_login_auth_002():
    setup_buyer()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "sai_pass"
    })
    assert resp.status_code == 401

def test_employee_login_auth_003():
    setup_buyer()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B999", "company_id": 1, "password": "123456"
    })
    assert resp.status_code == 401

def test_employee_login_auth_004():
    setup_buyer()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 99, "password": "123456"
    })
    assert resp.status_code == 401

def test_employee_login_and_me_001():
    setup_buyer()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    resp2 = client.get(f"/api/hrms/employee-login/me?token={token}")
    assert resp2.status_code == 200

def test_employee_login_and_me_002():
    setup_buyer()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    resp2 = client.get(f"/api/hrms/employee-login/me?token={token}")
    assert resp2.json()["employee_code"] == "B001"
    assert resp2.json()["company_id"] == 1
    assert resp2.json()["info"]["password"] == "123456"

def test_employee_login_and_me_003():
    setup_buyer()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    resp2 = client.get(f"/api/hrms/employee-login/me?token=token_sai")
    assert resp2.status_code == 401

def test_employee_login_info_001():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp2 = client.get("/api/hrms/employee-login/info?month=5&year=2025", headers=headers)
    assert resp2.status_code == 200

def test_employee_login_info_002():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp2 = client.get("/api/hrms/employee-login/info?month=5&year=2025", headers=headers)
    data = resp2.json()
    assert data["employee"]["name"] == "Test User"
    assert data["login"]["password"] == "123456"
    assert data["contract"]["contract"] == "HĐLĐ"
    assert data["attendance"]["days"] == 20
    assert data["shift"]["shift"] == "Sáng"
    assert data["project"]["project"] == "Dự án A"

def test_employee_login_info_003():
    setup_buyer_full()
    resp = client.post("/api/hrms/employee-login/auth", params={
        "employee_code": "B001", "company_id": 1, "password": "123456"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp2 = client.get("/api/hrms/employee-login/info?month=1&year=2024", headers=headers)
    assert resp2.status_code == 200
    data = resp2.json()
    # employee và login luôn có, các trường contract, attendance, shift, project phải None
    assert data["employee"]["name"] == "Test User"
    assert data["login"]["password"] == "123456"
    assert data["contract"] is None
    assert data["attendance"] is None
    assert data["shift"] is None
    assert data["project"] is None
