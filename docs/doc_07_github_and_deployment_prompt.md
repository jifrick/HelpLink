# HelpLink — GitHub & Deployment Specification
**Document ID:** DOC-07  
**Version:** 1.1  
**Status:** Approved Specification  
**Target Repository:** `helplink`  

---

## 1. Repository Structure & Configuration

```text
helplink/
├── .github/
│   └── workflows/
│       └── ci.yml              # Automated test suite on Push/PR
├── app/                        # Main FastAPI application code
├── tests/                      # Automated Pytest suite
├── docs/                       # Architecture & PRD specifications
├── .env.example                # Sample environment variables
├── .gitignore                  # Exclude venv, .pyc, *.db, .env
├── LICENSE                     # MIT Open Source License
├── README.md                   # Professional project documentation
├── requirements.txt            # Dependency specification
└── main.py                     # ASGI application runner
```

---

## 2. GitHub Actions CI Workflow (`.github/workflows/ci.yml`)

```yaml
name: HelpLink CI Pipeline

on:
  push:
    branches: [ main, develop, master ]
  pull_request:
    branches: [ main, develop, master ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Python Syntax & Compilation Verification
        run: |
          python -m py_compile main.py

      - name: Run Pytest Test Suite
        run: |
          pytest -v
```
