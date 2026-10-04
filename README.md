# HelpLink

HelpLink is an open-source, community-driven social-impact web platform designed to make useful resources, educational opportunities, scholarships, internships, entry-level jobs, free developer tools, volunteering opportunities, and community support programs easy to discover, organize, and share. Useful information is often fragmented across social channels and disparate websites; HelpLink aggregates these opportunities into a clean, searchable, community-moderated directory.

---

## 🌟 Key Features

- **🔍 Resource Discovery:** Instant access to public-interest opportunities across education, employment, scholarships, and community aid.
- **⚡ Search & Multi-Facet Filtering:** Keyword search across titles, descriptions, locations, categories, and tags, with location and resource-type filtering.
- **📝 Community Resource Submission:** User submission form with pre-submission community quality guidelines (*"Please only submit resources that are useful, legitimate, and appropriate for the community"*).
- **🔒 Authentication & User Roles:** Session-based cookie auth (`helplink_session`) and Bearer token JWT support for Role-Based Access Control (`Guest`, `User`, `Admin`).
- **❤️ Bookmarks & Saved Collections:** Logged-in users can bookmark resources to easily access them from their personal dashboard.
- **⚠️ Community Reporting:** Users can flag broken links, spam, outdated, or misleading content with specific report reason codes.
- **🛡️ Admin Moderation Dashboard:** Real-time metrics overview, pending submission queue with Approve/Reject/Archive actions, user report resolution, and category management.
- **🔌 RESTful API:** Complete v1 JSON REST endpoints (`/api/v1/resources`, `/api/v1/categories`, `/api/v1/auth`, `/api/v1/reports`, `/api/v1/admin`).
- **🛡️ Security & Input Sanitization:** Pydantic v2 data validation, `urllib.parse` URL scheme verification (`http://` / `https://` only), `nh3` HTML sanitization, passlib `pbkdf2_sha256` password hashing, and CSRF/Origin validation on state-changing POST operations.
- **📱 Responsive Public-Interest UI:** Accessible, mobile-first Vanilla CSS and JavaScript design system with generous spacing and high contrast.

---

## 🛠️ Tech Stack

- **Primary Language:** Python 3.11+
- **Web Framework:** FastAPI
- **ORM & Database Layer:** SQLAlchemy 2.0 | SQLite (Development) / PostgreSQL (Production ready)
- **Data Validation:** Pydantic v2
- **Templating & Frontend:** Jinja2 SSR | Vanilla CSS | Modern Vanilla JavaScript
- **Testing Suite:** Pytest | Pytest-Asyncio | HTTPX

---

## 🏗️ Architecture

HelpLink follows a strict layered, domain-driven monolithic architecture:

1. **Presentation Layer (`app/web/` & `app/api/`)**:
   - `web/`: Renders Jinja2 HTML templates for fast, SEO-indexed web pages.
   - `api/`: Exposes RESTful OpenAPI JSON endpoints for external client integrations.
2. **Business Logic Layer (`app/services/`)**:
   - Pure Python service modules (`resource_service`, `auth_service`, `moderation_service`, `report_service`, `category_service`, `utils`) containing all domain validation, query composition, and state changes.
3. **Data & ORM Layer (`app/models/` & `app/db/`)**:
   - SQLAlchemy 2.0 ORM mappings with declarative bases, foreign keys, indexes, and relationship cascades (`User`, `Category`, `Resource`, `Tag`, `SavedResource`, `Report`).
4. **Core Security & Configuration (`app/core/`)**:
   - Centralized constants, Pydantic settings management, password hashing, JWT encoding/decoding, and CSRF origin validation.

---

## 📁 Project Structure

```text
HelpLink/
├── app/
│   ├── core/           # Constants, Settings config, Security & JWT helpers
│   ├── db/             # SQLAlchemy engine, session maker, DB seeder script
│   ├── models/         # SQLAlchemy 2.0 ORM Database Models
│   ├── schemas/        # Pydantic v2 schemas and validation models
│   ├── services/       # Domain business logic & HTML sanitization
│   ├── web/            # Jinja2 HTML web routers and auth dependencies
│   ├── api/            # RESTful JSON API routers (v1)
│   ├── static/         # Custom CSS design system and JavaScript app scripts
│   └── templates/      # Jinja2 HTML layout containers, components, and views
├── tests/              # Automated Pytest suite (Auth, Moderation, Security, SEO, APIs)
├── .github/
│   └── workflows/
│       └── ci.yml      # GitHub Actions CI workflow
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusion rules
├── LICENSE             # MIT Open Source License
├── main.py             # ASGI Application Entry Point
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## 🚀 Local Development Setup

Follow these steps to run HelpLink on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/helplink.git
cd HelpLink
```

### 2. Create a Virtual Environment
```bash
# On Windows PowerShell
py -m venv venv
.\venv\Scripts\Activate.ps1

# On Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Initialize & Seed Database
```bash
python -m app.db.init_db
```

### 6. Start Development Server
```bash
python main.py
```
Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 7. Run Automated Tests
```bash
pytest -v
```

---

## ⚙️ Environment Variables

HelpLink uses `pydantic-settings` to load configuration from environment variables or a `.env` file:

```env
APP_NAME=HelpLink
ENV=development
DEBUG=True
SECRET_KEY=dev_secret_key_please_change_in_production_987654321
DATABASE_URL=sqlite:///./helplink.db
ADMIN_INITIAL_EMAIL=admin@helplink.org
ADMIN_INITIAL_PASSWORD=AdminDevPassword123!
```

> **Security Note:** Production environments (`ENV=production`) automatically require explicit non-default `SECRET_KEY` and `ADMIN_INITIAL_PASSWORD` settings.

---

## 🧪 Testing

The project includes an automated test suite using `pytest`:

```bash
pytest -v
```

Expected Output:
```text
17 passed in 2.13s
```

Testing coverage includes authentication workflows, RBAC admin authorization boundaries, URL scheme sanitization, resource submission validation, report logging, bookmarking, and REST API endpoints.

---

## 📖 API Documentation

FastAPI automatically generates interactive OpenAPI documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🛡️ Security Policy

- **Input Sanitization**: User-submitted content is sanitized via `nh3` to strip dangerous HTML tags and enforce `http://` and `https://` URL schemes.
- **CSRF Defense**: Origin and Referer header validation on state-changing POST/PUT/DELETE requests.
- **Secret Protection**: All credentials and secret keys must be supplied via environment variables. Secrets are excluded from version control via `.gitignore`.

---

## 🗺️ Project Roadmap

Future enhancements planned for subsequent releases:

### V2 Roadmap
- **Verified Organizations**: Verified badge system for trusted institutions and non-profits.
- **Saved Collections**: Ability for users to organize saved items into custom public/private folders.
- **Advanced Search Filters**: Filter by application deadlines and community verification score.

### V3 Roadmap
- **Location-Aware Discovery**: Geolocation-based resource matching.
- **Automated Expiry**: Expiry engine for time-bound events and scholarships.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
