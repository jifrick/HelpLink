# HelpLink — Technical Architecture Document
**Document ID:** DOC-02  
**Version:** 1.1  
**Status:** Approved Specification  
**Product:** HelpLink (Community Social-Impact Web Platform)  
**Primary Stack:** Python 3.11+ | FastAPI | SQLAlchemy 2.0 | Jinja2 | Modern CSS/JS | SQLite/PostgreSQL  

---

## 1. Executive Architecture Summary

HelpLink is engineered as a high-performance, SEO-friendly, monolithic Python application utilizing **FastAPI** for web routing, business logic, and API endpoints, combined with **Jinja2 SSR (Server-Side Rendering)** and **SQLAlchemy 2.0 ORM**.

This architectural choice delivers:
- **Instant load times & SEO indexability**: Server-rendered HTML with full OpenGraph/meta tag support.
- **Robust API Backend**: RESTful JSON endpoints alongside HTML routes for potential mobile app / PWA integration.
- **Strict Data Validation & Type Safety**: Pydantic v2 schemas across all data input and service boundaries.
- **Modular Monolith Layout**: Domain-driven directory organization for clean maintenance and scalability.

---

## 2. High-Level System Architecture

```
                                +-----------------------------------+
                                |            User Agent             |
                                |     (Browser / Mobile Web / SEO)  |
                                +-----------------------------------+
                                                  |
                                            HTTP / HTTPS
                                                  |
                                                  v
                                +-----------------------------------+
                                |        Uvicorn / FastAPI App      |
                                |                                   |
                                |  +-----------------------------+  |
                                |  | Middleware (CSRF, CORS, Auth)|  |
                                |  +-----------------------------+  |
                                |               |                   |
                                |       +-------+-------+           |
                                |       |               |           |
                                |       v               v           |
                                |  HTML Routers    API Routers      |
                                |  (Jinja2 SSR)    (JSON Specs)     |
                                |       |               |           |
                                |       +-------+-------+           |
                                |               |                   |
                                |               v                   |
                                |       Service Layer               |
                                |   (Business Logic & Validation)   |
                                |               |                   |
                                |               v                   |
                                |       SQLAlchemy 2.0 ORM          |
                                +-----------------------------------+
                                                  |
                                                  v
                                +-----------------------------------+
                                |       Relational Database         |
                                |  (SQLite Dev / PostgreSQL Prod)   |
                                +-----------------------------------+
```

---

## 3. Directory & Folder Structure

```text
helplink/
│
├── app/
│   ├── core/                   # Core application configuration & security
│   │   ├── constants.py        # Centralized canonical constants (Resource types, statuses, schemes)
│   │   ├── config.py           # Pydantic BaseSettings & Environment config
│   │   └── security.py         # Password hashing (passlib/pbkdf2_sha256) & JWT handling
│   │
│   ├── db/                     # Database connections & migrations
│   │   ├── session.py          # SQLAlchemy engine & sessionmaker
│   │   └── init_db.py          # Database seeder (Initial categories, demo resources, admin account)
│   │
│   ├── models/                 # SQLAlchemy ORM Database Models
│   │   ├── user.py             # User model (roles: Guest, User, Admin)
│   │   ├── category.py         # Category model
│   │   ├── resource.py         # Resource model (status: pending, published, rejected, archived)
│   │   ├── tag.py              # Tag & ResourceTag models
│   │   ├── saved_resource.py   # User bookmarked resources
│   │   └── report.py           # Flagged/Reported resources model
│   │
│   ├── schemas/                # Pydantic Schemas (Data Validation)
│   │   ├── user.py
│   │   ├── resource.py
│   │   ├── category.py
│   │   └── report.py
│   │
│   ├── services/               # Business Logic Layer
│   │   ├── auth_service.py     # Auth, session, password management
│   │   ├── resource_service.py # Resource CRUD, search, filter, pagination
│   │   ├── category_service.py # Category listing & metadata
│   │   ├── moderation_service.py# Admin moderation workflow
│   │   ├── report_service.py   # User reporting engine
│   │   └── utils.py            # Slugification, nh3 HTML sanitization, urllib URL parsing
│   │
│   ├── web/                    # HTML Server-Rendered Routers (Jinja2)
│   │   ├── dependencies.py     # Session Auth & CSRF/Origin validation
│   │   ├── views_public.py     # Homepage, Browse, Search, Category detail, Resource detail
│   │   ├── views_auth.py       # Login, Register, Logout views
│   │   ├── views_user.py       # User Dashboard, Saved resources, Submit resource
│   │   └── views_admin.py      # Moderation dashboard, Reports review, Resource edit
│   │
│   ├── api/                    # RESTful JSON API Routers (v1)
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── resources.py
│   │   │   ├── categories.py
│   │   │   ├── reports.py
│   │   │   └── admin.py
│   │   └── router.py
│   │
│   ├── static/                 # Static Assets
│   │   ├── css/
│   │   │   ├── main.css        # Core custom CSS design system & utilities
│   │   │   └── components.css  # Cards, nav, modals, forms styling
│   │   └── js/
│   │       └── app.js          # Interactive frontend enhancement
│   │
│   └── templates/              # Jinja2 HTML Templates
│       ├── layouts/            # Base layout container with header/footer
│       ├── components/         # Navbar, Cards, Modals, Footer
│       ├── public/             # Homepage, Resource detail, Browse/Search views
│       ├── auth/               # Login, Register pages
│       ├── user/               # Submit resource, Saved items, Profile
│       ├── admin/              # Dashboard, Pending items, Reports list
│       └── errors/             # 404, 500 pages
│
├── tests/                      # Automated Pytest Suite
├── docs/                       # Project Documentation & Specifications
├── .github/workflows/          # GitHub Actions CI Workflow
├── .env.example                # Template environment configuration
├── .gitignore
├── LICENSE                     # MIT Open Source License
├── README.md
├── requirements.txt
└── main.py                     # ASGI Application Entry Point
```
