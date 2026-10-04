def test_register_and_login(client):
    # 1. Register new user
    response = client.post(
        "/register",
        data={
            "full_name": "Test Contributor",
            "email": "contributor@example.com",
            "password": "Password123!"
        },
        follow_redirects=False
    )
    assert response.status_code == 303
    assert "helplink_session" in response.cookies

    # 2. Duplicate registration fails
    dup_res = client.post(
        "/register",
        data={
            "full_name": "Test Contributor",
            "email": "contributor@example.com",
            "password": "Password123!"
        }
    )
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.text

    # 3. Login with valid credentials
    login_res = client.post(
        "/login",
        data={
            "email": "contributor@example.com",
            "password": "Password123!"
        },
        follow_redirects=False
    )
    assert login_res.status_code == 303
    assert "helplink_session" in login_res.cookies

    # 4. Login with invalid credentials
    invalid_login = client.post(
        "/login",
        data={
            "email": "contributor@example.com",
            "password": "WrongPassword123!"
        }
    )
    assert invalid_login.status_code == 400
    assert "Invalid email or password" in invalid_login.text

def test_api_auth_login_and_me(client):
    # Register user
    client.post("/register", data={"full_name": "API User", "email": "apiuser@example.com", "password": "Password123!"})

    # Clear test client cookies to ensure clean Bearer header testing
    client.cookies.clear()

    # 1. API Login with valid credentials
    api_login = client.post("/api/v1/auth/login", json={"email": "apiuser@example.com", "password": "Password123!"})
    assert api_login.status_code == 200
    token_data = api_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 2. API /me with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    user_info = me_res.json()
    assert user_info["email"] == "apiuser@example.com"

    # 3. API /me unauthenticated
    client.cookies.clear()
    me_unauth = client.get("/api/v1/auth/me")
    assert me_unauth.status_code == 401

    # 4. API Login invalid credentials
    invalid_api = client.post("/api/v1/auth/login", json={"email": "apiuser@example.com", "password": "WrongPassword"})
    assert invalid_api.status_code == 401
