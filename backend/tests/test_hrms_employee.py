import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

EMPLOYEE_CODE = "E001"
COMPANY_ID = 1
MONTH = 5
YEAR = 2025

# --- Employee ---
def test_create_and_list_employee():
    data = {
        "employee_code": EMPLOYEE_CODE,
        "company_id": COMPANY_ID,
        "info": {"name": "Nguyen Van A", "dob": "1990-01-01"},
        "created_by": "admin"
    }
    res = client.post("/api/hrms/employee", json=data)
    assert res.status_code == 200
    emp = res.json()
    assert emp["employee_code"] == EMPLOYEE_CODE
    res = client.get(f"/api/hrms/employee?company_id={COMPANY_ID}")
    assert res.status_code == 200
    assert any(e["employee_code"] == EMPLOYEE_CODE for e in res.json())

# --- EmployeeLogin ---
def test_create_and_list_employee_login():
    data = {
        "employee_code": EMPLOYEE_CODE,
        "company_id": COMPANY_ID,
        "info": {"username": "E001", "password_hash": "hash"},
        "created_by": "admin"
    }
    res = client.post("/api/hrms/employee-login", json=data)
    assert res.status_code == 200
    login = res.json()
    assert login["employee_code"] == EMPLOYEE_CODE
    res = client.get(f"/api/hrms/employee-login?company_id={COMPANY_ID}")
    assert res.status_code == 200
    assert any(e["employee_code"] == EMPLOYEE_CODE for e in res.json())

# --- EmployeeContract ---
def test_create_and_list_employee_contract():
    data = {
        "employee_code": EMPLOYEE_CODE,
        "company_id": COMPANY_ID,
        "month": MONTH,
        "year": YEAR,
        "info": {"contract_type": "fulltime", "salary": 1000},
        "created_by": "admin"
    }
    res = client.post("/api/hrms/employee-contract", json=data)
    assert res.status_code == 200
    contract = res.json()
    assert contract["employee_code"] == EMPLOYEE_CODE
    res = client.get(f"/api/hrms/employee-contract?company_id={COMPANY_ID}&month={MONTH}&year={YEAR}")
    assert res.status_code == 200
    assert any(e["employee_code"] == EMPLOYEE_CODE for e in res.json())

# --- EmployeeAttendance ---
def test_create_and_list_employee_attendance():
    data = {
        "employee_code": EMPLOYEE_CODE,
        "company_id": COMPANY_ID,
        "month": MONTH,
        "year": YEAR,
        "info": {"days_present": 20, "days_absent": 2},
        "created_by": "admin"
    }
    res = client.post("/api/hrms/employee-attendance", json=data)
    assert res.status_code == 200
    att = res.json()
    assert att["employee_code"] == EMPLOYEE_CODE
    res = client.get(f"/api/hrms/employee-attendance?company_id={COMPANY_ID}&month={MONTH}&year={YEAR}")
    assert res.status_code == 200
    assert any(e["employee_code"] == EMPLOYEE_CODE for e in res.json())

# --- EmployeeShift ---
def test_create_and_list_employee_shift():
    data = {
        "employee_code": EMPLOYEE_CODE,
        "company_id": COMPANY_ID,
        "month": MONTH,
        "year": YEAR,
        "info": {"shift": "morning", "days": [1,2,3]},
        "created_by": "admin"
    }
    res = client.post("/api/hrms/employee-shift", json=data)
    assert res.status_code == 200
    shift = res.json()
    assert shift["employee_code"] == EMPLOYEE_CODE
    res = client.get(f"/api/hrms/employee-shift?company_id={COMPANY_ID}&month={MONTH}&year={YEAR}")
    assert res.status_code == 200
    assert any(e["employee_code"] == EMPLOYEE_CODE for e in res.json())

# --- EmployeeProject ---
def test_create_and_list_employee_project():
    data = {
        "employee_code": EMPLOYEE_CODE,
        "company_id": COMPANY_ID,
        "month": MONTH,
        "year": YEAR,
        "info": {"project": "ERP", "role": "dev"},
        "created_by": "admin"
    }
    res = client.post("/api/hrms/employee-project", json=data)
    assert res.status_code == 200
    project = res.json()
    assert project["employee_code"] == EMPLOYEE_CODE
    res = client.get(f"/api/hrms/employee-project?company_id={COMPANY_ID}&month={MONTH}&year={YEAR}")
    assert res.status_code == 200
    assert any(e["employee_code"] == EMPLOYEE_CODE for e in res.json())
