from app.services.resource_service import get_resources

def test_user_submission_and_admin_moderation(client, db):
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

    # Find the newly created published resource in DB
    published, _ = get_resources(db, status="published")
    assert len(published) > 0
    assert published[0].title == "Free React Native Mobile Workshop"
    new_res_id = published[0].id

    # 2. Login as Admin
    client.post("/login", data={"email": "admin@helplink.org", "password": "AdminDevPassword123!"})

    # 3. Admin dashboard should show published count
    dash_res = client.get("/admin/dashboard")
    assert dash_res.status_code == 200

    # 4. Admin approves resource
    approve_res = client.post(f"/admin/resources/{new_res_id}/status", data={"status": "published"}, follow_redirects=False)
    assert approve_res.status_code == 303

    # 5. Admin rejects resource
    reject_res = client.post(f"/admin/resources/{new_res_id}/status", data={"status": "rejected"}, follow_redirects=False)
    assert reject_res.status_code == 303

    # 6. Admin sends invalid status -> 400 Bad Request
    invalid_status = client.post(f"/admin/resources/{new_res_id}/status", data={"status": "invalid_status_key"})
    assert invalid_status.status_code == 400
    assert "Invalid resource status" in invalid_status.text
