"""Telegram bot command and message handlers."""

import re
from decimal import Decimal
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from sqlalchemy import select
from backend.app.bot.i18n import get_text
from backend.app.bot.keyboards import (
    get_language_keyboard,
    get_main_menu_keyboard,
    get_support_confirmation_keyboard,
)
from backend.app.ai.orchestrator import orchestrator
from backend.app.bot.session import (
    get_or_create_active_conversation,
    get_or_create_customer,
    save_message,
    update_customer_language,
)
from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.logging import logger
from backend.app.models.business import Business
from backend.app.models.category import Category
from backend.app.models.conversation import Conversation
from backend.app.models.knowledge import KnowledgeArticle
from backend.app.models.product import Product, ProductVariant
from backend.app.models.ticket import SupportTicket


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    async with AsyncSessionLocal() as db:
        customer = await get_or_create_customer(
            db,
            telegram_user_id=user.id,
            display_name=user.full_name or user.username,
            language_code=user.language_code,
        )
        conversation = await get_or_create_active_conversation(db, customer.id)
        await save_message(
            db,
            conversation_id=conversation.id,
            sender_type="customer",
            content="/start",
            message_type="command",
            telegram_message_id=update.message.message_id,
        )

        # Get business name
        res = await db.execute(select(Business).where(Business.id == settings.default_business_id))
        business = res.scalar_one_or_none()
        business_name = business.name if business else "NEXUS Store"

        welcome_text = get_text("welcome", customer.preferred_language, business_name=business_name)
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(customer.preferred_language),
        )

        # Prompt language selection inline on initial greeting
        await update.message.reply_text(
            get_text("choose_language", customer.preferred_language),
            reply_markup=get_language_keyboard(),
        )
        await db.commit()


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    if not update.effective_user or not update.message:
        return

    async with AsyncSessionLocal() as db:
        customer = await get_or_create_customer(db, telegram_user_id=update.effective_user.id)
        help_msg = get_text("help_text", customer.preferred_language)
        await update.message.reply_text(
            help_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(customer.preferred_language),
        )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command to refresh main navigation buttons."""
    if not update.effective_user or not update.message:
        return

    async with AsyncSessionLocal() as db:
        customer = await get_or_create_customer(db, telegram_user_id=update.effective_user.id)
        await update.message.reply_text(
            "📋 " + get_text("back_to_menu", customer.preferred_language),
            reply_markup=get_main_menu_keyboard(customer.preferred_language),
        )


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language change button or /lang command."""
    if not update.effective_user or not update.message:
        return

    async with AsyncSessionLocal() as db:
        customer = await get_or_create_customer(db, telegram_user_id=update.effective_user.id)
        await update.message.reply_text(
            get_text("choose_language", customer.preferred_language),
            reply_markup=get_language_keyboard(),
        )


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks (language selection, support confirmation)."""
    query = update.callback_query
    if not query or not query.data or not update.effective_user:
        return

    await query.answer()
    data = query.data

    async with AsyncSessionLocal() as db:
        customer = await get_or_create_customer(db, telegram_user_id=update.effective_user.id)
        conversation = await get_or_create_active_conversation(db, customer.id)

        # 1. Language selection callback
        if data.startswith("lang:"):
            selected_lang = data.split(":")[1]
            await update_customer_language(db, customer.id, selected_lang)
            await db.commit()

            ack_text = get_text("language_updated", selected_lang)
            if query.message:
                await query.message.reply_text(
                    ack_text,
                    reply_markup=get_main_menu_keyboard(selected_lang),
                )

        # 2. Support Escalation Confirmation
        elif data == "confirm_support":
            conversation.status = "awaiting_operator"
            # Create support ticket
            ticket = SupportTicket(
                business_id=settings.default_business_id,
                customer_id=customer.id,
                conversation_id=conversation.id,
                category="general",
                priority="high",
                status="open",
            )
            db.add(ticket)
            await save_message(
                db,
                conversation_id=conversation.id,
                sender_type="system",
                content="Customer requested human support operator.",
                message_type="handoff",
            )
            await db.commit()

            notice = get_text("operator_requested", customer.preferred_language)
            if query.message:
                await query.message.reply_text(notice, parse_mode=ParseMode.MARKDOWN)

        elif data == "cancel_support":
            if query.message:
                await query.message.reply_text(
                    get_text("back_to_menu", customer.preferred_language),
                    reply_markup=get_main_menu_keyboard(customer.preferred_language),
                )


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plain customer text messages and main menu buttons."""
    if not update.effective_user or not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    user_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        customer = await get_or_create_customer(
            db,
            telegram_user_id=user_id,
            display_name=update.effective_user.full_name,
            language_code=update.effective_user.language_code,
        )
        conversation = await get_or_create_active_conversation(db, customer.id)
        lang = customer.preferred_language

        # Persist customer message
        await save_message(
            db,
            conversation_id=conversation.id,
            sender_type="customer",
            content=user_text,
            telegram_message_id=update.message.message_id,
        )
        await db.commit()

        # If conversation is already handled by human operator, do not invoke AI!
        if conversation.status in ["awaiting_operator", "operator_active"]:
            notice = get_text("operator_already_active", lang)
            await update.message.reply_text(notice)
            return

        # Handle Menu Buttons
        # Products
        if user_text in [get_text("menu_products", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            await _handle_products_menu(update, db, lang)
            return

        # Search Products
        if user_text in [get_text("menu_search", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            await update.message.reply_text(
                get_text("ask_search_query", lang), parse_mode=ParseMode.MARKDOWN
            )
            return

        # My Orders
        if user_text in [get_text("menu_orders", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            await update.message.reply_text(
                get_text("ask_order_number", lang), parse_mode=ParseMode.MARKDOWN
            )
            return

        # Delivery Info
        if user_text in [get_text("menu_delivery", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            await _send_knowledge_topic(update, db, "delivery", lang)
            return

        # Returns & Warranty
        if user_text in [get_text("menu_warranty", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            await _send_knowledge_topic(update, db, "return_warranty", lang)
            return

        # FAQ
        if user_text in [get_text("menu_faq", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            await _send_faqs(update, db, lang)
            return

        # Contact Support
        if user_text in [get_text("menu_support", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            confirm_msg = (
                "Sizni operator bilan bog'lashimizni xohlaysizmi?"
                if lang == "uz"
                else (
                    "Хотите связаться с оператором поддержки?"
                    if lang == "ru"
                    else "Would you like to connect with a support representative?"
                )
            )
            await update.message.reply_text(
                confirm_msg, reply_markup=get_support_confirmation_keyboard(lang)
            )
            return

        # Language Settings
        if user_text in [get_text("menu_language", l) for l in ["uz", "ru", "en", "uz_cyrl"]]:
            await update.message.reply_text(
                get_text("choose_language", lang),
                reply_markup=get_language_keyboard(),
            )
            return

        # Natural Language / AI Query Handling (Connected to AI Subsystem in Milestone 3)
        await _handle_natural_language_query(update, db, conversation.id, user_text, lang)


async def _handle_products_menu(update: Update, db, lang: str) -> None:
    """Display catalog overview with verified products and prices in UZS."""
    result = await db.execute(
        select(Product)
        .where(
            Product.business_id == settings.default_business_id,
            Product.active_status.is_(True),
        )
        .limit(10)
    )
    products = result.scalars().all()

    if not products:
        await update.message.reply_text(get_text("no_products_found", lang))
        return

    lines = ["📱 *Demo Electronics mahsulotlari:*\n" if lang == "uz" else "📱 *Каталог товаров:*\n"]
    for p in products:
        # Fetch lowest price variant
        var_res = await db.execute(
            select(ProductVariant)
            .where(ProductVariant.product_id == p.id)
            .order_by(ProductVariant.price.asc())
        )
        variants = var_res.scalars().all()
        if variants:
            lowest = variants[0]
            formatted_price = f"{lowest.price:,.0f}".replace(",", " ")
            lines.append(f"• *{p.name}* ({p.brand}) — dan {formatted_price} {p.currency}")
        else:
            lines.append(f"• *{p.name}* ({p.brand})")

    lines.append(
        "\nBatafsil ma'lumot olish uchun mahsulot nomini yozing (masalan: *Samsung A16*):"
        if lang == "uz"
        else "\nДля подробностей напишите название товара (например: *Samsung A16*):"
    )

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def _send_knowledge_topic(update: Update, db, category: str, lang: str) -> None:
    """Send verified policy article."""
    res = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.business_id == settings.default_business_id,
            KnowledgeArticle.category == category,
            KnowledgeArticle.language == lang,
            KnowledgeArticle.is_active.is_(True),
        )
    )
    article = res.scalar_one_or_none()

    if not article:
        # Fallback to Uzbek or English
        res_fb = await db.execute(
            select(KnowledgeArticle).where(
                KnowledgeArticle.business_id == settings.default_business_id,
                KnowledgeArticle.category == category,
                KnowledgeArticle.is_active.is_(True),
            )
        )
        article = res_fb.scalar_one_or_none()

    if article:
        reply = f"📋 *{article.title}*\n\n{article.content}"
    else:
        reply = get_text("error_generic", lang)

    await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


async def _send_faqs(update: Update, db, lang: str) -> None:
    """Send list of active FAQs."""
    res = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.business_id == settings.default_business_id,
            KnowledgeArticle.category == "faq",
            KnowledgeArticle.language == lang,
            KnowledgeArticle.is_active.is_(True),
        )
    )
    faqs = res.scalars().all()

    if not faqs:
        await update.message.reply_text(get_text("error_generic", lang))
        return

    lines = ["❓ *Ko'p beriladigan savollar:*\n" if lang == "uz" else "❓ *Частые вопросы:*\n"]
    for faq in faqs:
        lines.append(f"*Q: {faq.title}*\n{faq.content}\n")

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def _handle_natural_language_query(
    update: Update, db, conversation_id: int, user_text: str, lang: str
) -> None:
    """Handle natural language inquiries through the AI orchestrator."""
    customer = await get_or_create_customer(db, telegram_user_id=update.effective_user.id)
    ai_response = await orchestrator.process_message(
        db=db,
        business_id=settings.default_business_id,
        customer_id=customer.id,
        conversation_id=conversation_id,
        user_message=user_text,
        lang=lang,
    )
    if ai_response.escalated_to_human:
        # Mark conversation as awaiting operator
        conv_res = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = conv_res.scalar_one_or_none()
        if conv:
            conv.status = "awaiting_operator"
            await db.commit()

    await update.message.reply_text(ai_response.text, parse_mode=ParseMode.MARKDOWN)
