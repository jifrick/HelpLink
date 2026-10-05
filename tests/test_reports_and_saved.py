def test_report_submission_and_resolution(client, db):
    # Register & Login user
    client.post("/register", data={"full_name": "Submitter", "email": "sub@test.org", "password": "Password123!"})
    # Submit resource
    client.post("/submit", data={"title": "Test Resource", "category_id": 1, "resource_type": "Course", "location": "Remote", "url": "https://example.org", "description": "This is a valid test resource description with enough length."})
    # Resource should be ID 1

    # 1. Submit a user report for resource ID 1
    report_res = client.post(
        "/resources/1/report",
        data={"reason": "broken_link", "details": "The link returns 404 error."},
        follow_redirects=False
    )
    assert report_res.status_code == 303

    # 2. Login as Admin
    client.post("/login", data={"email": "admin@helplink.org", "password": "AdminDevPassword123!"})

    # 3. Admin views reports
    admin_reports = client.get("/admin/reports")
    assert admin_reports.status_code == 200
    assert "broken_link" in admin_reports.text
    assert "The link returns 404 error." in admin_reports.text

    # 4. Admin updates report status
    update_res = client.post("/admin/reports/1/status", data={"status": "reviewed"}, follow_redirects=False)
    assert update_res.status_code == 303

def test_bookmark_saving_toggle(client, db):
    # Register & Login user
    client.post("/register", data={"full_name": "Bookmarker", "email": "bookmarker@test.org", "password": "Password123!"})
    
    # Submit resource
    client.post("/submit", data={"title": "National Post-Graduate Scholarship 2026", "category_id": 1, "resource_type": "Course", "location": "Remote", "url": "https://example.org", "description": "This is a valid test resource description with enough length."})

    # Toggle save on resource ID 1 -> Saved
    save_res = client.post("/resources/1/toggle-save")
    assert save_res.status_code == 200
    assert save_res.json()["saved"] is True

    # Check saved items page
    saved_page = client.get("/saved")
    assert saved_page.status_code == 200
    assert "National Post-Graduate Scholarship 2026" in saved_page.text

    # Toggle save again -> Unsaved
    unsave_res = client.post("/resources/1/toggle-save")
    assert unsave_res.status_code == 200
    assert unsave_res.json()["saved"] is False

def test_guest_cannot_save_resource(client, db):
    # Unauthenticated guest attempting to save resource -> 401 Unauthorized
    save_res = client.post("/resources/1/toggle-save")
    assert save_res.status_code == 401
