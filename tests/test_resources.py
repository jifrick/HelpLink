def test_homepage_and_browse(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "HelpLink" in res.text
    assert "National Post-Graduate Scholarship 2026" in res.text

    browse_res = client.get("/resources?q=Scholarship")
    assert browse_res.status_code == 200
    assert "National Post-Graduate Scholarship 2026" in browse_res.text

def test_resource_detail_view(client):
    res = client.get("/resources/national-post-graduate-scholarship-2026")
    assert res.status_code == 200
    assert "National Post-Graduate Scholarship 2026" in res.text
    assert "Visit External Resource" in res.text

def test_api_resources_and_categories_endpoints(client):
    res = client.get("/api/v1/resources")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] > 0

    cat_res = client.get("/api/v1/categories")
    assert cat_res.status_code == 200
    cats = cat_res.json()
    assert len(cats) >= 8
