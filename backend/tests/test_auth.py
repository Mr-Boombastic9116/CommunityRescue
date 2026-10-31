import uuid

def test_register_and_login_donor(client):
    unique_email = f"donor_{uuid.uuid4().hex[:8]}@test.com"
    reg_payload = {
        "name": "Test Donor Kitchen",
        "email": unique_email,
        "password": "SecretPassword123!",
        "role": "donor",
        "phone": "+91 9876543210",
        "organization_name": "Test Donor Kitchen Ltd",
        "address": "123 Food Street, Downtown",
    }

    # Register
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "donor"
    assert data["email"] == unique_email

    # Duplicate registration check
    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"]

    # Login
    login_payload = {
        "email": unique_email,
        "password": "SecretPassword123!",
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Fetch profile
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    profile = res_me.json()
    assert profile["email"] == unique_email
    assert profile["role"] == "donor"
    assert profile["profile"]["organization_name"] == "Test Donor Kitchen Ltd"

def test_invalid_login(client):
    res = client.post("/api/auth/login", json={"email": "nonexistent@test.com", "password": "wrongpassword"})
    assert res.status_code == 401

