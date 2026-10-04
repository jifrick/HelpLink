from app.core.constants import ALLOWED_RESOURCE_TYPES

def test_unauthorized_guest_access_to_admin(client):
    # Guests accessing /admin should be redirected to login / 401
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 401

    mod_res = client.get("/admin/moderation", follow_redirects=False)
    assert mod_res.status_code == 401

    # REST API guest protection
    api_pending = client.get("/api/v1/admin/pending")
    assert api_pending.status_code == 401

def test_regular_user_access_to_admin_forbidden(client):
    # Register regular user
    client.post("/register", data={"full_name": "Regular User", "email": "regular@test.org", "password": "Password123!"})
    
    # Attempt to access /admin -> should be 403 Forbidden
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 403

    # REST API regular user protection
    api_pending = client.get("/api/v1/admin/pending")
    assert api_pending.status_code == 403

def test_invalid_resource_submission_validation(client):
    # Register user
    client.post("/register", data={"full_name": "Test Submitter", "email": "submitter@test.org", "password": "Password123!"})

    # 1. Invalid Category ID (non-existent ID 9999)
    res_cat = client.post("/submit", data={
        "title": "Valid Resource Title",
        "category_id": 9999,
        "resource_type": "Course",
        "location": "Remote",
        "url": "https://example.org/course",
        "description": "A valid description of the resource that is long enough."
    })
    assert res_cat.status_code == 400
    assert "category does not exist" in res_cat.text

    # 2. Invalid Resource Type
    res_type = client.post("/submit", data={
        "title": "Valid Resource Title",
        "category_id": 1,
        "resource_type": "InvalidType",
        "location": "Remote",
        "url": "https://example.org/course",
        "description": "A valid description of the resource that is long enough."
    })
    assert res_type.status_code == 400
    assert "resource type is invalid" in res_type.text

    # 3. Invalid URL (missing http/https)
    res_url = client.post("/submit", data={
        "title": "Valid Resource Title",
        "category_id": 1,
        "resource_type": "Course",
        "location": "Remote",
        "url": "invalid-url-string",
        "description": "A valid description of the resource that is long enough."
    })
    assert res_url.status_code == 400
    assert "valid URL" in res_url.text

def test_all_valid_resource_types(client):
    client.post("/register", data={"full_name": "Type Tester", "email": "typetester@test.org", "password": "Password123!"})

    for rtype in ALLOWED_RESOURCE_TYPES:
        res = client.post("/submit", data={
            "title": f"Valid Title for {rtype}",
            "category_id": 1,
            "resource_type": rtype,
            "location": "Remote",
            "url": "https://example.org/test",
            "description": "A valid long description of the resource to pass minimum character checks."
        }, follow_redirects=False)
        assert res.status_code == 303

def test_security_url_validation(client):
    client.post("/register", data={"full_name": "URL Tester", "email": "urltester@test.org", "password": "Password123!"})

    invalid_urls = [
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "file:///etc/passwd",
        "vbscript:msgbox(1)",
        "ftp://example.com/file",
        "http://invalid_domain_no_dot"
    ]

    for bad_url in invalid_urls:
        res = client.post("/submit", data={
            "title": "Security Test Title",
            "category_id": 1,
            "resource_type": "Course",
            "location": "Remote",
            "url": bad_url,
            "description": "A valid description of the resource that is long enough."
        })
        assert res.status_code == 400

def test_csrf_origin_header_validation(client):
    client.post("/register", data={"full_name": "CSRF Tester", "email": "csrf@test.org", "password": "Password123!"})

    # Malicious cross-origin POST request
    res = client.post(
        "/submit",
        data={
            "title": "CSRF Test Title",
            "category_id": 1,
            "resource_type": "Course",
            "location": "Remote",
            "url": "https://example.org/test",
            "description": "A valid description of the resource that is long enough."
        },
        headers={"Origin": "https://malicious-website.com"}
    )
    assert res.status_code == 403
    assert "CSRF Protection" in res.text
