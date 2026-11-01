# NEXUS AI — Database Schema Specification
## Relational Data Model, Constraints, Indexes & Migrations

**Version:** 1.0.0  
**Engine:** SQLite (Development) / PostgreSQL 15+ (Production)  
**ORM:** SQLAlchemy 2.0 (Async)  
**Migration Tool:** Alembic  
**Target Market Standards:** Currency `UZS` (Uzbekistan Som, 2 decimal places), Timezone `Asia/Tashkent`

---

## 1. Entity-Relationship Overview

```
businesses (Tenant Root)
  ├── users (Operators, Admins, Owners, Viewers)
  ├── categories
  ├── products
  │     └── product_variants (SKU, Storage, Color, Price UZS, Stock)
  ├── customers
  │     ├── conversations
  │     │     ├── messages (Customer, AI, Operator, System, Internal Notes)
  │     │     └── support_tickets (Referenced by conversation)
  │     └── orders
  │           ├── order_items (Ref product_variants)
  │           └── order_status_history
  ├── knowledge_articles (FAQs, Policies, Operating Hours)
  ├── ai_settings (Gemini model parameters, limits, prompt overrides)
  └── audit_logs (Security-sensitive administrative mutations)
```

---

## 2. Table Specifications

### 2.1 `businesses`
Stores tenant profile, regional settings, and operating parameters.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer / BigInt | PK, Auto-increment | Unique business identifier |
| `name` | String(255) | NOT NULL | Business display name (e.g. "Demo Electronics") |
| `description` | Text | NULL | Business description |
| `primary_language` | String(10) | NOT NULL, DEFAULT 'uz' | 'uz' (Uzbek Latin), 'ru', 'en', 'uz_cyrl' |
| `supported_languages`| JSON | NOT NULL | List of active languages: `["uz", "ru", "en"]` |
| `timezone` | String(64) | NOT NULL, DEFAULT 'Asia/Tashkent' | Timezone identifier |
| `contact_information`| JSON | NULL | Phone numbers, address, support email |
| `working_hours` | JSON | NULL | Weekly schedules (e.g. Mon-Sat 09:00-19:00) |
| `active_status` | Boolean | NOT NULL, DEFAULT TRUE | Status toggle |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Record creation timestamp |
| `updated_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Record update timestamp |

### 2.2 `categories`
Hierarchical product catalog categories.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Category ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `name` | String(255) | NOT NULL | Category name (e.g. "Smartphones") |
| `slug` | String(255) | NOT NULL | URL-friendly identifier |
| `parent_id` | Integer | FK(`categories.id`), NULL | Parent category for nesting |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |

*Indexes:* `idx_categories_business_slug` (`business_id`, `slug`).

### 2.3 `products`
Product master catalog.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Product ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `category_id` | Integer | FK(`categories.id`), NULL | Category reference |
| `name` | String(255) | NOT NULL | Product name (e.g. "Samsung Galaxy A16") |
| `brand` | String(128) | NOT NULL | Brand (e.g. "Samsung", "Apple") |
| `description` | Text | NULL | Detailed specifications |
| `currency` | String(10) | NOT NULL, DEFAULT 'UZS' | Currency code |
| `active_status` | Boolean | NOT NULL, DEFAULT TRUE | Visibility toggle |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |
| `updated_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |

*Indexes:* `idx_products_business_brand` (`business_id`, `brand`), `idx_products_business_name` (`business_id`, `name`).

### 2.4 `product_variants`
Configurable stock keeping units (SKUs) with exact pricing and inventory.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Variant ID |
| `product_id` | Integer | FK(`products.id`), NOT NULL | Product reference |
| `sku` | String(128) | NOT NULL | Stock keeping unit (e.g. "SAM-A16-128-BLK") |
| `storage_capacity` | String(64) | NULL | e.g. "128 GB", "256 GB" |
| `color` | String(64) | NULL | e.g. "Black", "Light Blue" |
| `size` | String(64) | NULL | e.g. "Standard" |
| `attributes` | JSON | NULL | Arbitrary key-value technical specs |
| `price` | Numeric(14, 2) | NOT NULL | Decimal price in UZS (e.g. 2450000.00) |
| `stock_quantity` | Integer | NOT NULL, DEFAULT 0 | Real-time stock count |
| `availability_status`| String(32) | NOT NULL, DEFAULT 'in_stock' | 'in_stock', 'low_stock', 'out_of_stock' |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |
| `updated_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |

*Indexes:* `idx_variants_sku` (`sku`), `idx_variants_product` (`product_id`).

### 2.5 `customers`
Customer identity records. Data minimization enforced: only Telegram User ID and interaction preferences stored initially.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Customer ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `telegram_user_id` | BigInteger | NOT NULL | Unique Telegram User ID |
| `preferred_language` | String(10) | NOT NULL, DEFAULT 'uz' | Selected language |
| `display_name` | String(255) | NULL | Telegram first/last name or username |
| `phone_number` | String(32) | NULL | Optional verified contact |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Customer first contact |
| `last_interaction_at`| DateTime(UTC) | NOT NULL, DEFAULT utcnow | Last activity |

*Indexes:* `idx_customers_business_telegram` UNIQUE (`business_id`, `telegram_user_id`).

### 2.6 `conversations`
Support conversations representing customer sessions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Conversation ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `customer_id` | Integer | FK(`customers.id`), NOT NULL | Customer reference |
| `status` | String(32) | NOT NULL, DEFAULT 'ai_active' | 'ai_active', 'awaiting_operator', 'operator_active', 'closed' |
| `assigned_operator_id`| Integer | FK(`users.id`), NULL | Assigned support staff |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |
| `updated_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |
| `closed_at` | DateTime(UTC) | NULL | Session closure timestamp |

*Indexes:* `idx_conversations_status` (`business_id`, `status`), `idx_conversations_customer` (`customer_id`).

### 2.7 `messages`
Individual message records in a conversation.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Message ID |
| `conversation_id` | Integer | FK(`conversations.id`), NOT NULL | Conversation reference |
| `sender_type` | String(32) | NOT NULL | 'customer', 'ai', 'operator', 'system' |
| `content` | Text | NOT NULL | Message text |
| `message_type` | String(32) | NOT NULL, DEFAULT 'text' | 'text', 'button_click', 'handoff', 'note' |
| `telegram_message_id`| BigInteger | NULL | Telegram message sequence ID |
| `is_internal` | Boolean | NOT NULL, DEFAULT FALSE | TRUE = internal operator note |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |

*Indexes:* `idx_messages_conversation` (`conversation_id`, `created_at`).

### 2.8 `orders`, `order_items`, `order_status_history`
Order records for status lookup and customer verification.

```sql
-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    business_id INT NOT NULL REFERENCES businesses(id),
    customer_id INT NOT NULL REFERENCES customers(id),
    order_number VARCHAR(64) NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL DEFAULT 'pending', -- pending, confirmed, processing, shipping, delivered, cancelled
    total_amount NUMERIC(14, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'UZS',
    shipping_address TEXT NULL,
    recipient_phone VARCHAR(32) NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Order items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_variant_id INT NOT NULL REFERENCES product_variants(id),
    quantity INT NOT NULL DEFAULT 1,
    unit_price NUMERIC(14, 2) NOT NULL,
    total_price NUMERIC(14, 2) NOT NULL
);

-- Order status history
CREATE TABLE order_status_history (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL,
    notes TEXT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.9 `support_tickets`
Formal support escalation tickets.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Ticket ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `customer_id` | Integer | FK(`customers.id`), NOT NULL | Customer reference |
| `conversation_id` | Integer | FK(`conversations.id`), NULL | Associated conversation |
| `category` | String(64) | NOT NULL | 'product', 'delivery', 'return', 'complaint', 'general' |
| `priority` | String(32) | NOT NULL, DEFAULT 'medium' | 'low', 'medium', 'high', 'urgent' |
| `status` | String(32) | NOT NULL, DEFAULT 'open' | 'open', 'in_progress', 'resolved', 'closed' |
| `assigned_operator_id`| Integer | FK(`users.id`), NULL | Assigned operator |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Creation timestamp |
| `resolved_at` | DateTime(UTC) | NULL | Resolution timestamp |

### 2.10 `knowledge_articles`
Approved policies and FAQs.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Article ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `category` | String(64) | NOT NULL | 'faq', 'delivery', 'return_warranty', 'hours', 'payment', 'general' |
| `title` | String(255) | NOT NULL | Question / topic header |
| `content` | Text | NOT NULL | Verified response / policy body |
| `language` | String(10) | NOT NULL, DEFAULT 'uz' | 'uz', 'ru', 'en', 'uz_cyrl' |
| `version` | Integer | NOT NULL, DEFAULT 1 | Version counter |
| `is_active` | Boolean | NOT NULL, DEFAULT TRUE | Availability toggle |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |
| `updated_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |

### 2.11 `users`
Dashboard administration and support personnel.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | User ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `email` | String(255) | NOT NULL | Login email (unique per business) |
| `password_hash` | String(255) | NOT NULL | Argon2 / bcrypt hash |
| `full_name` | String(255) | NOT NULL | Operator / Admin full name |
| `role` | String(32) | NOT NULL | 'owner', 'admin', 'operator', 'viewer' |
| `is_active` | Boolean | NOT NULL, DEFAULT TRUE | Account active status |
| `created_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |

### 2.12 `ai_settings`
Configurable business-level AI parameters.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Setting ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL, UNIQUE | One setting per business |
| `model_name` | String(64) | NOT NULL, DEFAULT 'gemini-2.5-flash' | Gemini model identifier |
| `is_enabled` | Boolean | NOT NULL, DEFAULT TRUE | Global AI kill-switch |
| `temperature` | Float | NOT NULL, DEFAULT 0.2 | Sampling temperature |
| `max_output_tokens`| Integer | NOT NULL, DEFAULT 800 | Response length cap |
| `context_window_turns`| Integer | NOT NULL, DEFAULT 10 | Recent message count |
| `tool_call_limit` | Integer | NOT NULL, DEFAULT 5 | Max tool executions per query |
| `system_instructions`| Text | NULL | Custom business personality instructions |
| `escalation_rules`| JSON | NULL | Triggers for human escalation |
| `fallback_message` | Text | NULL | Safe response when AI is offline |
| `updated_at` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |

### 2.13 `audit_logs`
Immutable compliance and administrative action tracking.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Log ID |
| `business_id` | Integer | FK(`businesses.id`), NOT NULL | Tenant ID |
| `user_id` | Integer | FK(`users.id`), NULL | Actor ID (NULL if system/bot) |
| `action` | String(64) | NOT NULL | e.g. 'PRODUCT_UPDATE', 'POLICY_EDIT' |
| `resource_type` | String(64) | NOT NULL | e.g. 'product', 'ai_settings' |
| `resource_id` | String(64) | NULL | Target resource identifier |
| `outcome` | String(32) | NOT NULL | 'SUCCESS', 'FAILED', 'DENIED' |
| `ip_address` | String(45) | NULL | Origin IPv4/IPv6 |
| `details` | JSON | NULL | Diff or metadata |
| `timestamp` | DateTime(UTC) | NOT NULL, DEFAULT utcnow | Timestamp |
