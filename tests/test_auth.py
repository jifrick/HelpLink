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
