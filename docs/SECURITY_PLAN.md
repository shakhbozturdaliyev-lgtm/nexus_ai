# NEXUS AI — Security, Privacy & Defense Plan
## Comprehensive Threat Modeling, Guardrails & Access Controls

**Version:** 1.0.0  
**Author:** Cybersecurity & Security Engineering Team

---

## 1. Threat Modeling (STRIDE Analysis)

| Threat | System Vulnerability Vector | Defense Mechanism & Implementation |
|---|---|---|
| **Spoofing** | Attacker impersonates an admin or operator. | JWT authentication with strong secret key (`SESSION_SECRET`), short token expiration, bcrypt password hashing (work factor 12), and explicit role checks on every API endpoint. |
| **Tampering** | User alters order IDs or accesses another customer's data. | **Customer Context Verification**: Customer order lookups are strictly bound to `WHERE customer_id = :authenticated_customer_id AND business_id = :business_id`. Knowledge of an order number alone yields a 404 / access denied. |
| **Repudiation** | Operator denies modifying product pricing or AI prompts. | **Immutable Audit Logs**: All state mutations by authenticated users are recorded with user ID, IP address, timestamp, diff, and outcome in `audit_logs`. |
| **Information Disclosure** | Prompt injection forces Gemini to reveal API keys, prompts, or DB creds. | **Defense in Depth**: <br>1. Input sanitization strips prompt injection delimiters.<br>2. Secrets are never loaded into LLM system prompts or user turns.<br>3. Outbound regex scanner inspects AI responses and redacts credentials before Telegram transmission. |
| **Denial of Service** | Flooding Telegram bot or admin API with rapid updates. | In-memory token bucket rate limiters, per-user Telegram debounce, bounded retries with jitter, and strict request timeouts (FastAPI 30s, Gemini API 15s). |
| **Elevation of Privilege** | Support operator attempts to reconfigure AI settings or view audit logs. | Role-Based Access Control (RBAC): `Owner` > `Admin` > `Operator` > `Viewer`. Endpoints enforce granular role dependencies. |

---

## 2. Multi-Layer Prompt Injection Defense

Prompt injection is treated as untrusted user input across three discrete stages:

```
+-----------------------------------------------------------------------------+
| STAGE 1: INGESTION & SANITIZATION                                           |
| - Strip invisible unicode characters, zero-width spaces, and control tags.  |
| - Inspect for injection patterns: "ignore previous instructions",           |
|   "system prompt override", "act as DAN", "print your API key".             |
| - If high-confidence injection detected: route directly to standard canned  |
|   polite deflection without calling Gemini API (Zero Token Cost & 100% Safe)|
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| STAGE 2: ISOLATION & ALLOWLISTED TOOL CALLING                               |
| - System prompt strictly separates business facts from customer queries.    |
| - System prompts contain ZERO credentials, bot tokens, or DB passwords.     |
| - LLM is given strictly typed, read-only Pydantic tools.                     |
| - NO raw SQL execution, NO shell execution, NO eval/exec.                   |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| STAGE 3: OUTBOUND VERIFICATION & SECRET REDACTION                           |
| - Pre-delivery regex scan for: Telegram tokens (`[0-9]{8,10}:[a-zA-Z0-9_-]{35}`),|
|   Gemini keys (`AIza[0-9A-Za-z-_]{35}`), JWT signatures, and DB URLs.      |
| - Fact checker validates that prices and stock quantities in text match     |
|   the structured tool response. If hallucinated, replace with canned        |
|   safe verification message.                                                |
+-----------------------------------------------------------------------------+
```

---

## 3. Multi-Tenant Isolation

Multi-tenancy is guaranteed at the repository and service levels:
1. Every table (except system metadata) contains a non-nullable `business_id` foreign key.
2. The `business_id` is derived from the authenticated administrative session or Telegram business configuration.
3. Repositories automatically append `WHERE business_id = :business_id` to all `SELECT`, `UPDATE`, and `DELETE` operations.
4. Telegram updates verify that the bot token matches the configured `business_id`.

---

## 4. Sensitive Data Minimization & Privacy

- **Customer Privacy**: By default, the system only stores `telegram_user_id` and language preferences.
- **Operator Privacy**: Internal operator notes (`is_internal=True`) are flagged in the `messages` table and filtered out of any customer-facing queries or Telegram webhooks.
- **Log Masking**: Custom logging filter ensures tokens like `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`, and `SESSION_SECRET` are rendered as `***REDACTED***`.
