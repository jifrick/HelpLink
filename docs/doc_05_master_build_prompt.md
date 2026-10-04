# HelpLink — Master Build Instruction Set
**Document ID:** DOC-05  
**Version:** 1.1  
**Status:** Approved Specification  
**Target Application:** HelpLink (Community Social-Impact Platform)  

---

## Master System Build Directive

You are building **HelpLink**, a production-grade Python web application designed to connect people with useful community resources, scholarships, internships, free tools, volunteering opportunities, and courses.

### Core Build Directives
1. **Framework & Stack**: Python 3.11+, FastAPI, SQLAlchemy 2.0 ORM, Jinja2 Server-Side Rendering, Pydantic v2, SQLite (dev) / PostgreSQL (prod ready), custom Vanilla CSS & JS design system.
2. **Quality Benchmark**: Portfolio-ready, robust error handling, responsive mobile-first UI, high-contrast accessibility, zero generic placeholder styling.
3. **Execution Pipeline**:
   - Step 1: Initialize Virtual Environment (`py -m venv venv`) & install core dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `jinja2`, `python-multipart`, `passlib`, `python-jose`, `pytest`, `httpx`, `nh3`, `email-validator`).
   - Step 2: Establish file directory architecture (`app/core`, `app/db`, `app/models`, `app/schemas`, `app/services`, `app/web`, `app/api`, `app/templates`, `app/static`).
   - Step 3: Implement database models, migrations, and seeder script with pre-populated categories (`Education`, `Jobs`, `Internships`, `Scholarships`, `Volunteering`, `Community Support`, `Free Tools`, `Events`) and seed sample published resources.
   - Step 4: Implement core services (`resource_service`, `auth_service`, `moderation_service`, `report_service`).
   - Step 5: Implement HTML Web Routers (`views_public.py`, `views_auth.py`, `views_user.py`, `views_admin.py`).
   - Step 6: Create high-aesthetic HTML templates with CSS design system (Hero, Search, Category Cards, Resource Detail, Moderation Dashboard, Submission Form, Toasts, Modals).
   - Step 7: Write unit & integration test suite (`tests/`).
   - Step 8: Execute app locally and verify all user & admin workflows.
