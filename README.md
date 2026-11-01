# NEXUS AI — Intelligent Telegram Customer Support Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-Proprietary-indigo.svg)]()

> **NEXUS AI** is an enterprise-grade, modular, multilingual customer support automation platform designed for businesses in Uzbekistan. Combining Telegram’s conversational reach with Google Gemini’s reasoning and deterministic backend safeguards, NEXUS AI automates product inquiries, stock verification, and order tracking without hallucinating.

---

## 🌟 Key Capabilities

1. **Multilingual Telegram Support**: Native fluency in **Uzbek (Latin & Cyrillic)**, **Russian**, and **English**.
2. **Deterministic Fact Guardrail**: Product prices (in UZS), inventory counts, and order statuses are verified directly against database records before delivery. Fabricated answers are strictly prevented.
3. **Dual AI Engine Architecture**:
   - **Google Gen AI SDK**: Uses `google.genai` with function calling (`gemini-2.5-flash`).
   - **Offline Mock Engine**: Zero-dependency fallback allowing 100% offline development with 0 API cost.
4. **Human Operator Escalation**: Smooth handoff with ticket creation, AI silence locks, live Telegram reply bridge, and confidential internal notes.
5. **Modern SaaS Admin Console**: React 18 single-page dashboard featuring 12 operational views and a 3-column operator workspace.
6. **Robust Security & Privacy**: Tenant isolation, bcrypt hashing, JWT authentication, customer order privacy checks, and prompt injection defense.

---

## 🏗️ System Architecture

```
Telegram User (UZ / RU / EN)
          │
          ▼
python-telegram-bot (Async Polling / Webhook)
          │
          ▼
FastAPI Gateway & Auth Service
          │
     ┌────┴──────────────────────────┐
     ▼                               ▼
AI Orchestrator               Support Service (Human Handoff)
- Prompt Injection Shield     - Ticket Generation
- Gemini Function Calling     - Operator Claim & Live Reply
- Deterministic Guardrails    - Internal Operator Notes
     │                               │
     └───────────────┬───────────────┘
                     ▼
         SQLAlchemy 2.0 Async ORM
         (SQLite Dev / Postgres Prod)
                     │
                     ▼
             Admin Web Console
      (React + Vite + Tailwind CSS)
```

---

## 🚀 Quick Start on Windows 11

### 1. Backend & Bot Setup
```powershell
# Create and activate virtual environment
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt

# Configure environment
Copy-Item .env.example .env

# Run FastAPI backend (Port 8000)
uvicorn backend.app.main:app --reload --port 8000

# In a separate terminal, start Telegram bot runner
python scripts\run_bot.py
```

### 2. Frontend Dashboard Setup
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open [http://localhost:5173](http://localhost:5173).  
**Default Credentials:** `admin@demoelectronics.uz` / `AdminPass123!`

---

## 🧪 Automated Testing

NEXUS AI includes a comprehensive test suite covering Unit, Integration, API, Security, and all 6 E2E scenarios:

```powershell
.\backend\.venv\Scripts\pytest.exe -c backend\pytest.ini backend\tests
```
**Result**: 47 passed in ~7s with 100% success.

---

## 📂 Project Directory Structure

```
nexus-ai/
├── backend/
│   ├── app/
│   │   ├── ai/            # Gemini SDK, Mock Engine, Guardrails, Tools
│   │   ├── api/           # FastAPI REST Routers (Auth, Products, Chats, etc.)
│   │   ├── bot/           # Telegram Bot handlers, i18n, keyboards, session
│   │   ├── core/          # Config, Async DB, Security, Rate limiting, Logging
│   │   ├── database/      # Seeding script with Demo Electronics catalog
│   │   ├── models/        # 15 SQLAlchemy 2.0 entities
│   │   ├── services/      # Domain logic (Support escalation service)
│   │   └── main.py        # Application entrypoint & health checks
│   ├── tests/             # 47 automated test cases
│   └── requirements.txt   # Locked dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI (Sidebar, Header)
│   │   ├── pages/         # 12 Operational views (3-column chat console, etc.)
│   │   ├── services/      # Typed API client
│   │   └── types/         # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── docs/                  # Architecture, Database Schema, Security, Roadmap
├── scripts/               # Standalone runner scripts (run_bot.py)
├── .env.example           # Environment template
├── docker-compose.yml     # Multi-container deployment configuration
└── README.md              # Project documentation
```

---

## 📋 Documentation Index

- [Project Plan](docs/PROJECT_PLAN.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Security & Privacy Plan](docs/SECURITY_PLAN.md)
- [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md)
- [Testing Strategy & Scenarios](docs/TESTING_STRATEGY.md)
- [Windows 11 Setup Guide](SETUP_WINDOWS.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
