# HelpLink — Testing & QA Specification
**Document ID:** DOC-06  
**Version:** 1.1  
**Status:** Approved Specification  
**Target Application:** HelpLink (Community Social-Impact Platform)  

---

## 1. Testing Strategy & Framework

Testing is mandatory for HelpLink to ensure security, data integrity, and error-free user navigation.

- **Test Runner**: `pytest`
- **Async Test Support**: `pytest-asyncio`
- **API & SSR Test Client**: `httpx.AsyncClient` or FastAPI `TestClient`
- **Database Isolation**: In-memory SQLite session fixtures initialized before each test run and torn down afterwards.

---

## 2. Test Suite Categories

### 2.1 Authentication & Authorization Tests
- User Registration (valid data, duplicate email prevention, password hashing validation).
- User Login & Logout (correct credentials, invalid credentials, session cookie setting).
- Access Control: Guest blocked from submitting resource or accessing `/admin/dashboard`.
- Admin Protection: Only user with `role == 'admin'` can access moderation endpoints.

### 2.2 Resource Service & Search Tests
- Submission Workflow: New submission created with status `pending`.
- Moderation Actions: Admin approves submission -> status transitions to `published` -> appears in public search.
- Moderation Rejection: Admin rejects submission -> status transitions to `rejected` -> excluded from public search.
- Multi-Field Keyword Search: Search for "Python", "Scholarship", or location returns matching published resources.
- Filter Combinations: Category + Resource Type + Location filtering.
- Pagination: Verify page limits and total counts.

### 2.3 User Interaction Tests
- Bookmark/Save Resource: User can save/unsave resources; view list in personal dashboard.
- Report Resource: Guest/User can flag broken links or misleading info with specific reasons.

### 2.4 Form & Input Validation Tests
- Invalid URL validation (rejects `javascript:`, `data:`, `file:`, `vbscript:`, malformed URLs).
- Required field validation (empty title, missing category, description under 20 chars).
- XSS Prevention: Malformed HTML script tags in descriptions are sanitized before storage/rendering.
