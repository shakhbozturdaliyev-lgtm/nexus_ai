"""Database initialization and demonstration data seeding."""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, Base, async_engine
from backend.app.core.logging import logger
from backend.app.core.security import get_password_hash
from backend.app.models.ai_setting import AISetting
from backend.app.models.business import Business
from backend.app.models.category import Category
from backend.app.models.knowledge import KnowledgeArticle
from backend.app.models.product import Product, ProductVariant
from backend.app.models.user import User


async def init_db() -> None:
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")


async def seed_data() -> None:
    """Seed initial demonstration data for Demo Electronics."""
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if Demo Electronics business already exists
        result = await session.execute(select(Business).where(Business.id == 1))
        existing_business = result.scalar_one_or_none()

        if existing_business:
            logger.info("Database already seeded with Demo Electronics (Business ID: 1).")
            return

        logger.info("Seeding demonstration catalog and knowledge base for Demo Electronics...")

        # 1. Create Business
        business = Business(
            id=1,
            name="Demo Electronics",
            description="Leading electronics retailer in Tashkent, Uzbekistan.",
            primary_language="uz",
            supported_languages=["uz", "ru", "en", "uz_cyrl"],
            timezone="Asia/Tashkent",
            contact_information={
                "phone": "+998 71 200 00 00",
                "email": "support@demoelectronics.uz",
                "address": "Tashkent, Amir Temur avenue 107",
                "telegram": "@demoelectronics_support",
            },
            working_hours={
                "monday_saturday": "09:00 - 20:00",
                "sunday": "Closed",
            },
            active_status=True,
        )
        session.add(business)
        await session.flush()

        # 2. Categories
        cat_smartphones = Category(business_id=business.id, name="Smartphones", slug="smartphones")
        cat_laptops = Category(business_id=business.id, name="Laptops", slug="laptops")
        cat_accessories = Category(business_id=business.id, name="Accessories", slug="accessories")
        session.add_all([cat_smartphones, cat_laptops, cat_accessories])
        await session.flush()

        # 3. Products & Variants
        # 3.1 Samsung Galaxy A16
        prod_samsung = Product(
            business_id=business.id,
            category_id=cat_smartphones.id,
            name="Samsung Galaxy A16",
            brand="Samsung",
            description="6.7-inch Super AMOLED 90Hz display, 50MP camera, 5000mAh battery.",
            currency="UZS",
            active_status=True,
        )
        session.add(prod_samsung)
        await session.flush()

        var_sam_1 = ProductVariant(
            product_id=prod_samsung.id,
            sku="SAM-A16-128-BLK",
            storage_capacity="128 GB",
            color="Black",
            price=Decimal("2450000.00"),
            stock_quantity=15,
            availability_status="in_stock",
        )
        var_sam_2 = ProductVariant(
            product_id=prod_samsung.id,
            sku="SAM-A16-256-BLU",
            storage_capacity="256 GB",
            color="Light Blue",
            price=Decimal("2850000.00"),
            stock_quantity=8,
            availability_status="in_stock",
        )
        session.add_all([var_sam_1, var_sam_2])

        # 3.2 Apple iPhone 16
        prod_apple = Product(
            business_id=business.id,
            category_id=cat_smartphones.id,
            name="Apple iPhone 16",
            brand="Apple",
            description="A18 chip, Camera Control, 48MP Fusion camera, Action button.",
            currency="UZS",
            active_status=True,
        )
        session.add(prod_apple)
        await session.flush()

        var_app_1 = ProductVariant(
            product_id=prod_apple.id,
            sku="IPH-16-128-BLU",
            storage_capacity="128 GB",
            color="Ultramarine",
            price=Decimal("12800000.00"),
            stock_quantity=10,
            availability_status="in_stock",
        )
        var_app_2 = ProductVariant(
            product_id=prod_apple.id,
            sku="IPH-16-256-BLK",
            storage_capacity="256 GB",
            color="Black",
            price=Decimal("14200000.00"),
            stock_quantity=6,
            availability_status="in_stock",
        )
        session.add_all([var_app_1, var_app_2])

        # 3.3 Xiaomi Redmi Note 13
        prod_xiaomi = Product(
            business_id=business.id,
            category_id=cat_smartphones.id,
            name="Xiaomi Redmi Note 13",
            brand="Xiaomi",
            description="108MP triple camera, 120Hz FHD+ AMOLED display, 33W fast charge.",
            currency="UZS",
            active_status=True,
        )
        session.add(prod_xiaomi)
        await session.flush()

        var_xiao = ProductVariant(
            product_id=prod_xiaomi.id,
            sku="XIA-RN13-128-BLK",
            storage_capacity="128 GB",
            color="Midnight Black",
            price=Decimal("2100000.00"),
            stock_quantity=25,
            availability_status="in_stock",
        )
        session.add(var_xiao)

        # 3.4 Lenovo IdeaPad 3
        prod_lenovo = Product(
            business_id=business.id,
            category_id=cat_laptops.id,
            name="Lenovo IdeaPad 3 15IAU7",
            brand="Lenovo",
            description="Intel Core i3-1215U, 8GB RAM, 512GB SSD NVMe, 15.6 FHD IPS.",
            currency="UZS",
            active_status=True,
        )
        session.add(prod_lenovo)
        await session.flush()

        var_len = ProductVariant(
            product_id=prod_lenovo.id,
            sku="LEN-IP3-512-GRY",
            storage_capacity="512 GB SSD",
            color="Platinum Grey",
            price=Decimal("4900000.00"),
            stock_quantity=5,
            availability_status="in_stock",
        )
        session.add(var_len)

        # 4. Knowledge Base Articles
        articles = [
            # Delivery Policy (UZ, RU, EN)
            KnowledgeArticle(
                business_id=business.id,
                category="delivery",
                title="Yetkazib berish shartlari",
                content=(
                    "Toshkent shahri bo'ylab yetkazib berish 1 kun ichida amalga oshiriladi. "
                    "500,000 so'mdan yuqori buyurtmalar uchun Toshkentda yetkazib berish bepul! "
                    "500,000 so'mdan kam buyurtmalar uchun yetkazib berish narxi 25,000 so'm. "
                    "O'zbekiston viloyatlariga yetkazib berish 2-3 ish kuni davomida amalga oshiriladi "
                    "va narxi 35,000 so'm."
                ),
                language="uz",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="delivery",
                title="Условия доставки",
                content=(
                    "Доставка по Ташкенту осуществляется в течение 1 дня. "
                    "При заказе на сумму свыше 500,000 сум доставка по Ташкенту бесплатная. "
                    "До 500,000 сум — 25,000 сум. "
                    "Доставка по регионам Узбекистана занимает 2-3 рабочих дня, стоимость 35,000 сум."
                ),
                language="ru",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="delivery",
                title="Delivery Terms",
                content=(
                    "Delivery in Tashkent is completed within 1 business day. "
                    "Delivery is FREE in Tashkent for orders exceeding 500,000 UZS. "
                    "For orders below 500,000 UZS, delivery is 25,000 UZS. "
                    "Regional delivery across Uzbekistan takes 2-3 business days at a flat rate of 35,000 UZS."
                ),
                language="en",
            ),
            # Return and Warranty (UZ, RU, EN)
            KnowledgeArticle(
                business_id=business.id,
                category="return_warranty",
                title="Kafolat va qaytarish shartlari",
                content=(
                    "Barcha smartfon va noutbuklarimizga 1 yillik rasmiy ishlab chiqaruvchi kafolati beriladi. "
                    "Xaridor xarid qilingan kundan boshlab 14 kun ichida tovarni qaytarish yoki almashtirish huquqiga ega. "
                    "Bunda tovarning asl qadog'i, kvitansiyasi va shikastlanmagan tovar ko'rinishi saqlangan bo'lishi shart."
                ),
                language="uz",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="return_warranty",
                title="Гарантия и возврат товара",
                content=(
                    "На всю электронику предоставляется 1 год официальной сервисной гарантии. "
                    "Возврат или обмен товара возможен в течение 14 дней со дня покупки, "
                    "если сохранены товарный вид, заводские пломбы, упаковка и чек."
                ),
                language="ru",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="return_warranty",
                title="Warranty and Return Policy",
                content=(
                    "All products include an official 1-year manufacturer warranty. "
                    "Customers may return or exchange products within 14 days of purchase, "
                    "provided packaging, tags, accessories, and proof of purchase are intact."
                ),
                language="en",
            ),
            # Operating Hours (UZ, RU, EN)
            KnowledgeArticle(
                business_id=business.id,
                category="hours",
                title="Ish tartibi",
                content=(
                    "Bizning do'konimiz dushanbadan shanbagacha soat 09:00 dan 20:00 gacha xizmat ko'rsatadi. "
                    "Yakshanba — dam olish kuni. Onlayn buyurtmalar har kuni 24/7 qabul qilinadi."
                ),
                language="uz",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="hours",
                title="Часы работы",
                content=(
                    "Наш магазин работает с понедельника по субботу с 09:00 до 20:00. "
                    "Воскресенье — выходной. Онлайн-заказы в боте принимаются круглосуточно 24/7."
                ),
                language="ru",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="hours",
                title="Business Hours",
                content=(
                    "Our retail showroom is open Monday through Saturday from 09:00 to 20:00. "
                    "Sunday: Closed. Online orders and bot inquiries are accepted 24/7."
                ),
                language="en",
            ),
            # FAQ: Payment (UZ, RU, EN)
            KnowledgeArticle(
                business_id=business.id,
                category="faq",
                title="Qanday to'lov turlari mavjud?",
                content=(
                    "To'lovlarni kurerga naqd pul orqali, shuningdek Payme, Click va Uzum Bank "
                    "ilovalaridan foydalangan holda amalga oshirishingiz mumkin."
                ),
                language="uz",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="faq",
                title="Способы оплаты",
                content=(
                    "Мы принимаем оплату наличными курьеру при получении, "
                    "а также онлайн-переводы через Payme, Click и Uzum Bank."
                ),
                language="ru",
            ),
            KnowledgeArticle(
                business_id=business.id,
                category="faq",
                title="What payment methods do you accept?",
                content=(
                    "We accept cash on delivery as well as instant transfers via Payme, Click, and Uzum Bank."
                ),
                language="en",
            ),
        ]
        session.add_all(articles)

        # 5. Default Administrative Users
        admin_user = User(
            business_id=business.id,
            email="admin@demoelectronics.uz",
            password_hash=get_password_hash("AdminPass123!"),
            full_name="Demo Administrator",
            role="owner",
            is_active=True,
        )
        operator_user = User(
            business_id=business.id,
            email="operator@demoelectronics.uz",
            password_hash=get_password_hash("OperatorPass123!"),
            full_name="Nodir Karimov",
            role="operator",
            is_active=True,
        )
        session.add_all([admin_user, operator_user])

        # 6. Default AI Settings
        ai_setting = AISetting(
            business_id=business.id,
            model_name="gemini-2.5-flash",
            is_enabled=True,
            temperature=0.2,
            max_output_tokens=800,
            context_window_turns=10,
            tool_call_limit=5,
            system_instructions=(
                "You are NEXUS AI, an intelligent customer support assistant for Demo Electronics in Uzbekistan. "
                "Always verify products, prices, and stock using your tools. "
                "Never guess or invent prices. "
                "Respond helpfully in the customer's language (Uzbek, Russian, or English)."
            ),
            escalation_rules={
                "escalate_on_missing_price": True,
                "escalate_on_user_request": True,
                "max_consecutive_clarifications": 3,
            },
            fallback_message=(
                "Kechirasiz, tizimda vaqtincha texnik yangilanish ketmoqda. "
                "Operatorimiz tez orada siz bilan bog'lanadi."
            ),
        )
        session.add(ai_setting)

        await session.commit()
        logger.info("Demo Electronics data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())
