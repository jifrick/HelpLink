from app.services.utils import sanitize_html

def test_html_sanitization_rules():
    # 1. Strip script tags
    dirty_script = "<script>alert('xss')</script><p>Hello world</p>"
    clean = sanitize_html(dirty_script)
    assert "<script>" not in clean
    assert "Hello world" in clean

    # 2. Add rel="noopener noreferrer" to external links
    link_html = '<a href="https://example.org" target="_blank">External Site</a>'
    clean_link = sanitize_html(link_html)
    assert 'rel="noopener noreferrer"' in clean_link
    assert 'href="https://example.org"' in clean_link

    # 3. Reject unsafe URI schemes in link href
    js_link = '<a href="javascript:alert(1)">Click me</a>'
    clean_js = sanitize_html(js_link)
    assert "javascript:" not in clean_js

def test_resource_detail_seo_metadata(client, db):
    client.post("/register", data={"full_name": "Submitter", "email": "seo@test.org", "password": "Password123!"})
    client.post("/submit", data={"title": "National Post-Graduate Scholarship 2026", "category_id": 1, "resource_type": "Course", "location": "Remote", "url": "https://example.org", "description": "This is a valid test resource description with enough length."})

    res = client.get("/resources/national-post-graduate-scholarship-2026")
    assert res.status_code == 200
    html = res.text

    # Resource-specific title
    assert "<title>National Post-Graduate Scholarship 2026 — HelpLink</title>" in html

    # Resource-specific OpenGraph meta tags
    assert 'content="National Post-Graduate Scholarship 2026 — HelpLink Community Network"' in html
    assert 'content="This is a valid test resource description' in html

    # Accessible external CTA link attributes
    assert 'rel="noopener noreferrer"' in html
    assert 'aria-label="Visit external website for National Post-Graduate Scholarship 2026"' in html
