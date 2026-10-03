def test_user_submission_and_admin_moderation(client):
    # 1. Register user & submit resource
    client.post("/register", data={"full_name": "Submitter", "email": "user@test.org", "password": "Password123!"})
    
    sub_res = client.post("/submit", data={
        "title": "Free React Native Mobile Workshop",
        "category_id": 1,
        "resource_type": "Course",
        "location": "Kozhikode",
        "url": "https://example.org/react-native",
        "description": "A comprehensive 2-day free hands-on workshop building cross-platform apps."
    }, follow_redirects=False)
    assert sub_res.status_code == 303

    # 2. Login as Admin
    client.post("/login", data={"email": "admin@helplink.org", "password": "AdminSecurePassword123!"})

    # 3. Check moderation queue
    mod_res = client.get("/admin/moderation")
    assert mod_res.status_code == 200
    assert "Free React Native Mobile Workshop" in mod_res.text
