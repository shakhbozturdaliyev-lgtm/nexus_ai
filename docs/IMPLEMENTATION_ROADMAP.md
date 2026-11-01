# NEXUS AI — Implementation Roadmap
## Incremental Milestones, Deliverables & Acceptance Criteria

**Version:** 1.0.0  
**Methodology:** Incremental, Test-Driven Verification

---

## Milestone 1: Foundation (Current Sprint)
**Objective:** Deliver clean, modular backend scaffolding, database models, configuration, migrations, seeds, logging, and health endpoints.

- **Deliverables:**
  - Project directory structure (`backend/app`, `frontend/src`, `docs/`, `scripts/`).
  - Configuration management via `pydantic-settings` with `.env.example`.
  - SQLAlchemy 2.0 Async database engine (`sqlite+aiosqlite` dev, `postgresql+asyncpg` prod).
  - All 15 database models with relationships, indexes, and constraints.
  - Seeding utility with complete demo catalog for "Demo Electronics" (smartphones, laptops, accessories in UZS, policies in UZ/RU/EN, admin user).
  - FastAPI application entrypoint with health and readiness checks.
  - Pytest foundation suite verifying database initialization and seeding.
- **Acceptance Criteria:**
  - `pytest backend/tests` executes and passes 100%.
  - Health check endpoint `/api/health` returns `{"status": "ok", "database": "connected"}`.

---

## Milestone 2: Telegram Bot MVP
**Objective:** Deliver a responsive, multilingual Telegram bot interface with persistent sessions and intuitive menus.

- **Deliverables:**
  - `python-telegram-bot` 21+ async polling integration.
  - Greeting workflow on `/start` with language picker (Uzbek Latin, Uzbek Cyrillic, Russian, English).
  - Persistent reply keyboard for main menu:
    - Products / Maxsulotlar / Продукты
    - Search Products / Qidiruv / Поиск товаров
    - My Orders / Buyurtmalarim / Мои заказы
    - Delivery Info / Yetkazib berish / Доставка
    - Returns & Warranty / Qaytarish va Kafolat / Возврат и гарантия
    - FAQ / Ko'p beriladigan savollar / Частые вопросы
    - Contact Support / Operator bilan bog'lanish / Связаться с оператором
    - Language Settings / Tilni o'zgartirish / Язык
  - Multi-turn conversation tracker and customer registry.
  - Telegram integration test suite with mocked updates.
- **Acceptance Criteria:**
  - Bot successfully connects via token or runs in test simulation mode.
  - All menus render correctly in the selected language.

---

## Milestone 3: AI Intelligence Engine & Guardrails
**Objective:** Deliver intelligent decision-making, Google Gen AI SDK integration, deterministic tool execution, and local Mock AI fallback.

- **Deliverables:**
  - Gen AI SDK client wrapper with configurable Gemini models (`gemini-2.5-flash`, etc.).
  - Offline Mock AI engine allowing full end-to-end functionality without an API key.
  - 10 narrowly scoped Pydantic tools for catalog, inventory, orders, knowledge, and tickets.
  - Hallucination guardrail validating prices and availability against the database snapshot.
  - Prompt injection defense and outbound secret leak scanner.
  - Multi-turn conversation sliding context window.
  - AI unit and integration test suite.
- **Acceptance Criteria:**
  - Product queries accurately report database prices and stock.
  - Missing catalog items trigger honest fallback rather than made-up prices.
  - Prompt injection attempts are neutralized safely.

---

## Milestone 4: Human Escalation & Support Operations
**Objective:** Enable seamless handoff from AI to human operators with ticket lifecycle management.

- **Deliverables:**
  - Escalation rule engine (human requested, missing price, complaint, repeated tool failures).
  - Support ticket creation with category, priority, and operator assignment.
  - AI silence lock when conversation is awaiting operator or operator active.
  - Live operator-to-Telegram messaging bridge.
  - Operator internal notes (`is_internal=True`) isolated from customer view.
  - Ticket resolution and return-to-AI transition flow.
  - Support workflow test suite.
- **Acceptance Criteria:**
  - Escalation triggers transition conversation to `awaiting_operator`.
  - Operator replies reach the customer's Telegram chat.

---

## Milestone 5: Admin Management Dashboard
**Objective:** Deliver a commercial-grade React web dashboard for operators and business managers.

- **Deliverables:**
  - React 18 + Vite + TypeScript + Tailwind CSS application.
  - JWT authentication flow with role-based routing (`Owner`, `Admin`, `Operator`, `Viewer`).
  - 12 core dashboard views:
    1. Overview (real metrics, active chats, tickets, AI usage)
    2. Conversations (3-column live operator console)
    3. Customers (directory, language, history)
    4. Products (catalog, variant matrix, UZS pricing, stock, CSV import/export)
    5. Orders (order list, status manager, verification)
    6. Support Tickets (ticket board, priority, assignment)
    7. Knowledge Base (multilingual FAQs, delivery/return policy editor)
    8. Analytics (response times, resolution rates, AI costs)
    9. AI Settings (model, temperature, system prompt, escalation rules)
    10. Team Members (operator/admin accounts, roles)
    11. Business Settings (company info, working hours, timezone)
    12. Audit Logs (immutable action log)
- **Acceptance Criteria:**
  - Frontend builds with zero TypeScript errors.
  - All 12 pages render with responsive layouts, loading states, and mock/live API data.

---

## Milestone 6: Reliability, Security Hardening & Performance
**Objective:** Harden the platform with retries, rate limiting, audit logging, and stress testing.

- **Deliverables:**
  - Bounded retries with exponential backoff and jitter for external calls.
  - Rate limiting on API and Telegram handlers.
  - Structured request logging with correlation IDs.
  - Full automated test suite execution (Unit, Integration, Security, E2E).
- **Acceptance Criteria:**
  - Test suite passes with high coverage.
  - Zero unhandled exceptions during API or bot failure simulations.

---

## Milestone 7: Production Packaging & Deployment Preparation
**Objective:** Provide containerization, Windows 11 local dev documentation, and deployment guides.

- **Deliverables:**
  - Multi-stage Dockerfile for Backend and Frontend.
  - `docker-compose.yml` for unified local/prod setup.
  - `SETUP_WINDOWS.md`, `README.md`, `TROUBLESHOOTING.md`, `.env.example`.
  - Final verification against all 15 Definition of Done criteria.
- **Acceptance Criteria:**
  - Single command starts services cleanly in Docker or on Windows PowerShell.
