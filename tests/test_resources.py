def test_homepage_and_browse(client, db):
    client.post("/register", data={"full_name": "Submitter", "email": "sub@test.org", "password": "Password123!"})
    client.post("/submit", data={"title": "National Post-Graduate Scholarship 2026", "category_id": 1, "resource_type": "Course", "location": "Remote", "url": "https://example.org", "description": "This is a valid test resource description with enough length."})

    res = client.get("/")
    assert res.status_code == 200
    assert "HelpLink" in res.text
    assert "National Post-Graduate Scholarship 2026" in res.text

    browse_res = client.get("/resources?q=Scholarship")
    assert browse_res.status_code == 200
    assert "National Post-Graduate Scholarship 2026" in browse_res.text

def test_resource_detail_view(client, db):
    client.post("/register", data={"full_name": "Submitter2", "email": "sub2@test.org", "password": "Password123!"})
    client.post("/submit", data={"title": "National Post-Graduate Scholarship 2026", "category_id": 1, "resource_type": "Course", "location": "Remote", "url": "https://example.org", "description": "This is a valid test resource description with enough length."})

    res = client.get("/resources/national-post-graduate-scholarship-2026")
    assert res.status_code == 200
    assert "National Post-Graduate Scholarship 2026" in res.text
    assert "Visit External Resource" in res.text

def test_api_resources_and_categories_endpoints(client, db):
    client.post("/register", data={"full_name": "Submitter3", "email": "sub3@test.org", "password": "Password123!"})
    client.post("/submit", data={"title": "National Post-Graduate Scholarship 2026", "category_id": 1, "resource_type": "Course", "location": "Remote", "url": "https://example.org", "description": "This is a valid test resource description with enough length."})

    res = client.get("/api/v1/resources")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] > 0

    cat_res = client.get("/api/v1/categories")
    assert cat_res.status_code == 200
    cats = cat_res.json()
    assert len(cats) >= 8
