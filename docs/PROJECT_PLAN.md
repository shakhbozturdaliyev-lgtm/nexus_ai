# NEXUS AI — Project Plan
## Intelligent Telegram Customer Support Platform

**Version:** 1.0.0  
**Target Market:** Uzbekistan  
**Primary Channels:** Telegram Bot, Web Admin Dashboard  
**Supported Languages:** Uzbek (Latin & Cyrillic), Russian, English  
**Default Currency:** UZS (Uzbekistan Som)  
**Default Timezone:** Asia/Tashkent (UTC+5)

---

## 1. Executive Summary & Objective

NEXUS AI is an enterprise-grade, modular, multilingual customer support automation platform designed for modern businesses. Combining Telegram’s conversational reach with Google Gemini’s reasoning capabilities and deterministic backend business safeguards, NEXUS AI automates product inquiries, stock verification, order lookups, and business policy questions without hallucinating.

When customer inquiries exceed AI boundaries or require human intervention, the system smoothly escalates conversations to human support operators through a real-time web administration dashboard.

---

## 2. Core Stakeholders & Personas

| Persona | Role | Primary Goals & Workflows |
|---|---|---|
| **Customer** | Telegram User | Inquires about products, prices, stock, delivery, orders, and policies in Uzbek, Russian, or English; requests human assistance when needed. |
| **Support Operator** | Web Console User | Receives escalated tickets, views full conversation transcripts, answers live via Telegram gateway, adds private internal notes, resolves tickets. |
| **Catalog Manager / Admin** | Web Console User | Manages products, variants, SKU inventory, prices, policies, FAQs, and business operating hours. |
| **Business Owner / Super Admin**| Web Console User | Configures AI prompts, model parameters, escalation rules, monitors analytics, audit logs, and invites team members. |
| **System / Developer** | Engineering | Maintains system uptime, monitors API costs and performance, deploys updates via Docker Compose and migrations. |

---

## 3. Scope of Work

### In Scope
1. **Multilingual Telegram Bot**:
   - Interactive `/start` flow with language selection (Uzbek Latin, Uzbek Cyrillic, Russian, English).
   - Dynamic reply keyboards and inline menus.
   - Natural language comprehension in all three languages.
   - Context maintenance over multi-turn conversations.
2. **AI Engine with Guardrails**:
   - Google Gen AI SDK (`google-genai`) integration with configurable Gemini models (`gemini-2.5-flash`, etc.).
   - Structured tool/function calling for catalog, inventory, orders, and knowledge base.
   - Built-in Mock AI Engine for local offline execution without credentials.
   - Deterministic verification of prices and availability before returning answers to customers.
   - Prompt injection defense, secret redacting, and conversation context windowing.
3. **Multi-Tenant Relational Database**:
   - SQLAlchemy 2.0 Async ORM with SQLite (development) and PostgreSQL (production).
   - Alembic migration pipeline.
   - 15 core entities covering businesses, products, variants, customers, conversations, messages, orders, tickets, knowledge base, users, ai settings, and audit logs.
4. **Human Handoff & Support Workflow**:
   - Automatic triggers (policy exceptions, human requests, tool failures, missing prices).
   - Ticket generation and operator notification.
   - Live two-way chat between operator dashboard and customer Telegram chat.
   - Internal notes invisible to customers.
5. **Administrative Web Dashboard**:
   - React + TypeScript + Vite + Tailwind CSS.
   - 12 comprehensive modules: Overview, Conversations, Customers, Products, Orders, Support Tickets, Knowledge Base, Analytics, AI Settings, Team Members, Business Settings, Audit Logs.
   - 3-column operator console.
6. **Production & Local Development Readiness**:
   - Docker and Docker Compose definitions.
   - Complete Windows 11 setup guide and scripts.
   - Automated tests (unit, integration, security, end-to-end scenarios).

### Explicitly Out of Scope (Phase 1)
- Payment gateway processing (Click / Payme / Uzum integration planned for future release).
- Vector databases, Redis, Celery, or Kubernetes (system is intentionally lightweight and zero-dependency bloat).

---

## 4. Key Performance Indicators (KPIs) & Quality Targets

- **Accuracy**: 100% deterministic accuracy for product prices, stock availability, and order status. Zero tolerated hallucinations.
- **Latency**: Sub-1.5s response time for direct menu queries; sub-3.0s response time for Gemini reasoning with tool execution.
- **Reliability**: Graceful fallback with user-friendly notices when external APIs (Telegram or Gemini) encounter rate limits or outages.
- **Security**: Complete multi-tenant isolation, strict RBAC, and zero leakage of system instructions, keys, or cross-customer data.
- **Local Developer Experience**: First-time setup on Windows 11 executable in under 5 minutes with zero paid prerequisites.

---

## 5. Milestone Delivery Schedule

```
+-----------------------------------------------------------------------------------+
| Milestone 1: Foundation (Config, Async DB, Models, Migrations, Seed, Health)      |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| Milestone 2: Telegram Bot MVP (PTB, i18n, Menus, Sessions, Mock Responders)       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| Milestone 3: AI Intelligence Engine (Gemini SDK, Tools, Guardrails, Mock AI)      |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| Milestone 4: Human Escalation & Support Operations (Tickets, Handoff, Chat Bridge)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| Milestone 5: Admin Dashboard (React, Vite, Tailwind, 12 Core Views, JWT Auth)     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| Milestone 6: Reliability, Security Hardening & Performance Testing                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| Milestone 7: Production Packaging, Docker, Acceptance Testing & Final Docs        |
+-----------------------------------------------------------------------------------+
```
