import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_org_register_and_employee_management(gateway_client: AsyncClient):
    # 1. Register a new Enterprise Organization
    org_payload = {
        "company_name": "Apex Legal Solutions Pvt Ltd",
        "domain": "apexlegal.in",
        "admin_name": "Advocate Rajesh Sharma",
        "admin_email": "admin@apexlegal.in",
        "admin_password": "CompanySecret123!"
    }
    response = await gateway_client.post("/api/v1/org/register", json=org_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user_info"]["role"] == "COMPANY_ADMIN"
    assert data["user_info"]["organization_name"] == "Apex Legal Solutions Pvt Ltd"

    admin_token = data["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Add Employee under the Organization
    emp_payload = {
        "email": "employee.priya@apexlegal.in",
        "full_name": "Priya Verma",
        "password": "EmpPassword123!",
        "department": "Corporate Legal",
        "role": "EMPLOYEE"
    }
    emp_response = await gateway_client.post("/api/v1/org/employees/add", json=emp_payload, headers=admin_headers)
    assert emp_response.status_code == 200
    emp_data = emp_response.json()
    assert emp_data["employee"]["email"] == "employee.priya@apexlegal.in"
    assert emp_data["employee"]["role"] == "EMPLOYEE"

    # 3. List Employees in the Organization
    list_response = await gateway_client.get("/api/v1/org/employees", headers=admin_headers)
    assert list_response.status_code == 200
    team = list_response.json()
    assert isinstance(team, list)
    assert len(team) >= 2
    emails = [e["email"] for e in team]
    assert "admin@apexlegal.in" in emails
    assert "employee.priya@apexlegal.in" in emails

    # 4. Login as Employee
    login_resp = await gateway_client.post(
        "/api/v1/auth/login",
        data={"username": "employee.priya@apexlegal.in", "password": "EmpPassword123!"}
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["user_info"]["role"] == "EMPLOYEE"
    assert login_data["user_info"]["organization_name"] == "Apex Legal Solutions Pvt Ltd"
