import pytest
from httpx import AsyncClient
from services.gateway.auth import verify_password, get_password_hash, create_access_token
from jose import jwt
from services.gateway.config import settings

@pytest.mark.asyncio
async def test_password_hashing():
    raw_pass = "LegalSecret123!"
    hashed = get_password_hash(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

@pytest.mark.asyncio
async def test_jwt_token_generation():
    payload = {"sub": "lawyer@leximini.in"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "lawyer@leximini.in"
    assert "exp" in decoded

@pytest.mark.asyncio
async def test_user_register_and_login(gateway_client: AsyncClient):
    # 1. Register a new user
    user_payload = {
        "email": "advocate.sharma@leximini.in",
        "password": "SecurePassword123",
        "full_name": "Advocate Sharma"
    }
    response = await gateway_client.post("/api/v1/auth/register", json=user_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # 2. Duplicate registration attempt
    dup_response = await gateway_client.post("/api/v1/auth/register", json=user_payload)
    assert dup_response.status_code == 400
    assert dup_response.json()["detail"] == "Email already registered"

    # 3. Login with correct credentials
    login_response = await gateway_client.post(
        "/api/v1/auth/login",
        data={"username": "advocate.sharma@leximini.in", "password": "SecurePassword123"}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data

    # 4. Login with invalid password
    invalid_login = await gateway_client.post(
        "/api/v1/auth/login",
        data={"username": "advocate.sharma@leximini.in", "password": "WrongPassword"}
    )
    assert invalid_login.status_code == 400
