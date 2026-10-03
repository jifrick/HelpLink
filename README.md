# HelpLink — Community Resource Network 🤝

> **Connect people with useful resources.**

HelpLink is an open-source, community-driven web platform designed to make useful resources, educational opportunities, scholarships, internships, entry-level jobs, free tools, and local support programs easy to discover, organize, and share.

---

## 🌟 Key Features

- **🔍 Discovery First:** Instant multi-field keyword search across titles, descriptions, categories, and locations.
- **📂 Categorized Directory:** 8 core public-interest categories (`Education`, `Jobs`, `Internships`, `Scholarships`, `Volunteering`, `Community Support`, `Free Tools`, `Events`).
- **🛡️ Community Moderation:** Admin dashboard with pending submission queues, approval/rejection workflows, and user flag reporting.
- **👤 User Management:** Authentication, personalized user dashboard, saved bookmarks, and submission tracking.
- **⚡ High-Performance Architecture:** FastAPI + Jinja2 Server-Side Rendering (SSR) for instant loading, full SEO metadata, and zero framework bloat.
- **📱 Responsive Public-Interest Design:** Mobile-first, high-contrast accessible UI system.

---

## 🛠️ Tech Stack

- **Backend Framework:** Python 3.11+ | FastAPI
- **Database & ORM:** SQLAlchemy 2.0 ORM | SQLite (Dev) / PostgreSQL (Prod)
- **Templating & Frontend:** Jinja2 SSR | Modern Custom Vanilla CSS & JS
- **Security & Validation:** Pydantic v2 | Passlib (Bcrypt) | Argon2 | nh3 HTML Sanitization
- **Testing Suite:** Pytest | Pytest-Asyncio | HTTPX

---

## 📁 Repository Structure

```text
HelpLink/
├── app/
│   ├── core/           # Config, security, password hashing, JWT/session logic
│   ├── db/             # SQLAlchemy engine, session maker, DB seeder script
│   ├── models/         # ORM entities (User, Category, Resource, Tag, Report, SavedResource)
│   ├── schemas/        # Pydantic validation schemas
│   ├── services/       # Domain business logic (Search, CRUD, Moderation, Reporting)
│   ├── web/            # Server-rendered HTML routers (Jinja2)
│   ├── api/            # RESTful JSON API endpoints
│   ├── static/         # Custom CSS design system, components, app JS
│   └── templates/      # Jinja2 layouts, components, public views, admin dashboard
├── tests/              # Automated unit and integration test suite
├── .env.example        # Environment configuration template
├── main.py             # ASGI FastAPI application entry point
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

---

## 🚀 Local Setup & Installation

### 1. Prerequisites
- Python 3.11+ installed on your system.
- Git.

### 2. Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/your-username/helplink.git
cd HelpLink

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux / macOS)
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

Default local `.env` settings:
```env
APP_NAME=HelpLink
ENV=development
DEBUG=True
SECRET_KEY=helplink_dev_secret_key_change_in_prod_2026_987654321
DATABASE_URL=sqlite:///./helplink.db
ADMIN_INITIAL_EMAIL=admin@helplink.org
ADMIN_INITIAL_PASSWORD=AdminSecurePassword123!
```

### 5. Run the Application

```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

Open your browser and navigate to:
- **Web App:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Specs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Admin Login:** Credentials set in `.env` (`admin@helplink.org` / `AdminSecurePassword123!`)

---

## 🧪 Running Automated Tests

HelpLink includes a complete Pytest automated test suite:

```bash
pytest -v
```

---

## 🛡️ License

MIT License &copy; 2026 HelpLink Contributors.
