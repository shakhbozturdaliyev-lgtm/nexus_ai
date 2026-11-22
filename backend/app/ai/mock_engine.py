"""Zero-dependency Offline Mock AI Engine for testing, local execution, and free customer dialogue."""

import re
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.ai.schemas import AIResponse
from backend.app.ai.tools import (
    tool_check_inventory,
    tool_create_order,
    tool_create_support_ticket,
    tool_get_business_hours,
    tool_get_delivery_policy,
    tool_get_faq_answer,
    tool_get_order_status,
    tool_get_return_policy,
    tool_search_products,
)
from backend.app.core.logging import logger


class MockAIEngine:
    """Intelligent conversational AI engine with deterministic tool dispatch, free dialogue, and order placement."""

    async def generate_response(
        self,
        db: AsyncSession,
        business_id: int,
        customer_id: int,
        conversation_id: int,
        user_message: str,
        lang: str = "uz",
        history: List[Dict[str, str]] = None,
    ) -> AIResponse:
        """Process customer query using natural dialogue, recommendations, and tool dispatch."""
        clean_text = user_message.lower().strip()
        tool_calls = []

        # 0. Intent: Polite Greetings & Pleasantries
        greeting_words = {
            "salom", "assalomu alaykum", "assalom", "qalesiz", "yaxshimisiz", "hayrli kun",
            "hayrli tong", "hayrli kech", "privet", "привет", "здравствуйте", "здравствуй",
            "добрый день", "доброе утро", "добрый вечер", "hello", "hi", "hey", "good morning", "good afternoon"
        }
        if clean_text in greeting_words or any(clean_text.startswith(gw) for gw in ["assalom", "salom", "здравств", "привет"]):
            greeting_replies = {
                "uz": (
                    "Assalomu alaykum! Demo Electronics rasmiy do'konining intellektual yordamchisiga xush kelibsiz! 😊\n\n"
                    "Men sizga do'konimizdagi barcha texnikalar bo'yicha erkin yordam bera olaman:\n"
                    "• Smartfonlar (Samsung Galaxy, Apple iPhone, Xiaomi Redmi)\n"
                    "• Noutbuklar (Lenovo IdeaPad) va aksessuarlar\n"
                    "• Qulay narxlar va modellarni taqqoslash\n"
                    "• Muddatli to'lov (nasiya) va bepul yetkazib berish\n"
                    "• To'g'ridan-to'g'ri buyurtma rasmiylashtirish\n\n"
                    "Bugun sizga qaysi mahsulot yoki xizmatimiz bo'yicha yordam bera olaman?"
                ),
                "ru": (
                    "Здравствуйте! Добро пожаловать в интеллектуальную службу поддержки Demo Electronics! 😊\n\n"
                    "Я с удовольствием проконсультирую вас по любым вопросам:\n"
                    "• Смартфоны (Samsung Galaxy, Apple iPhone, Xiaomi Redmi)\n"
                    "• Ноутбуки Lenovo и аксессуары\n"
                    "• Подбор модели, сравнение характеристик и цен\n"
                    "• Рассрочка без первоначального взноса и бесплатная доставка\n"
                    "• Быстрое оформление заказа прямо здесь\n\n"
                    "Какой товар или вопрос вас интересует сегодня?"
                ),
                "en": (
                    "Hello! Welcome to Demo Electronics intelligent customer support! 😊\n\n"
                    "I am delighted to assist you freely with any inquiries:\n"
                    "• Smartphones (Samsung Galaxy, Apple iPhone, Xiaomi Redmi)\n"
                    "• Laptops (Lenovo IdeaPad) and accessories\n"
                    "• Expert product recommendations and price comparisons\n"
                    "• 0% installment plans and free express delivery across Tashkent\n"
                    "• Direct order placement right here in chat\n\n"
                    "How may I assist you with our catalog today?"
                ),
            }
            return AIResponse(
                text=greeting_replies.get(lang, greeting_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=50,
            )

        # 0.5 Intent: Gratitude & Polite Closing
        thanks_words = {"rahmat", "katta rahmat", "spasibo", "спасибо", "благодарю", "thanks", "thank you"}
        if any(tw in clean_text for tw in thanks_words):
            thanks_replies = {
                "uz": (
                    "Arzimaydi! Sizga xizmat ko'rsatishdan mamnunmiz. 😊\n"
                    "Agar yana biron bir savolingiz bo'lsa yoki yangi buyurtma bermoqchi bo'lsangiz, doimo yordamga tayyorman. "
                    "Kuningiz xayrli va barakali o'tsin!"
                ),
                "ru": (
                    "Пожалуйста! Всегда рады помочь вам. 😊\n"
                    "Если возникнут еще вопросы или захотите оформить заказ, обращайтесь в любое время. "
                    "Желаем отличного настроения и приятных покупок!"
                ),
                "en": (
                    "You are very welcome! It is a pleasure to assist you. 😊\n"
                    "Feel free to reach out anytime if you need more details or wish to place an order. "
                    "Have a wonderful day!"
                ),
            }
            return AIResponse(
                text=thanks_replies.get(lang, thanks_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=40,
            )

        # 1. Intent: Human Operator Request
        if any(w in clean_text for w in ["operator", "inson", "menejer", "mutaxassis", "оператор", "человек", "менеджер", "human", "agent", "support"]):
            ticket_res = await tool_create_support_ticket(
                db=db,
                business_id=business_id,
                customer_id=customer_id,
                category="general",
                message=user_message,
                conversation_id=conversation_id,
            )
            tool_calls.append({"tool": "create_support_ticket", "result": ticket_res})

            replies = {
                "uz": "👨‍💼 Sizning so'rovingiz qabul qilindi va mutaxassisga yo'naltirildi. Operatorimiz tez orada siz bilan bog'lanadi.",
                "ru": "👨‍💼 Ваш запрос принят и передан оператору. Специалист поддержки скоро ответит вам.",
                "en": "👨‍💼 Your request has been forwarded to a customer support specialist. We will reply shortly.",
            }
            return AIResponse(
                text=replies.get(lang, replies["uz"]),
                tool_calls_made=tool_calls,
                escalated_to_human=True,
                language_used=lang,
                tokens_used=120,
            )

        # 2. Intent: Order Placement / Direct Purchase Workflow (NEW)
        # Check if customer expresses intent to order OR supplies phone/address to complete an order
        order_intent_keywords = [
            "buyurtma ber", "buyurtma qil", "sotib ol", "zakaz ber", "zakaz qil", "xarid qil",
            "olmoqchiman", "olmoqchiman", "zakaz qilmoqchi", "buyurtma qilmoqchi", "buyurtma bermoqchi",
            "order now", "place order", "i want to buy", "purchase",
            "купить", "заказать", "оформить заказ", "хочу заказать", "хочу купить"
        ]
        has_order_intent = any(k in clean_text for k in order_intent_keywords)
        phone_match = re.search(r"(\+?998\s?[0-9]{2}\s?[0-9]{3}\s?[0-9]{2}\s?[0-9]{2}|[0-9]{9,12})", user_message)

        if has_order_intent or phone_match:
            # Check if this turn is purely looking up an existing order number like ORD-1001
            is_lookup_query = bool(re.search(r"\bORD-\d+\b", user_message, re.IGNORECASE)) or any(
                w in clean_text for w in ["status", "holati", "qayerda qoldi", "buyurtmam holati", "статус"]
            )

            if not is_lookup_query:
                # 2.1 Determine target product from current message OR conversation history
                target_product = None
                target_variant = None

                # First search current message for a product
                search_res = await tool_search_products(db=db, business_id=business_id, query=clean_text)
                if search_res.get("products"):
                    target_product = search_res["products"][0]
                    if target_product.get("variants"):
                        target_variant = target_product["variants"][0]

                # If no product found in current message, look back at recent conversation history
                if not target_product and history:
                    for turn in reversed(history):
                        prev_content = turn.get("content", "").lower()
                        prev_search = await tool_search_products(db=db, business_id=business_id, query=prev_content)
                        if prev_search.get("products"):
                            target_product = prev_search["products"][0]
                            if target_product.get("variants"):
                                target_variant = target_product["variants"][0]
                            break

                # Fallback to default flagship if none specified
                if not target_product:
                    cat_res = await tool_search_products(db=db, business_id=business_id, query="samsung s23 ultra")
                    if cat_res.get("products"):
                        target_product = cat_res["products"][0]
                        if target_product.get("variants"):
                            target_variant = target_product["variants"][0]

                p_name = target_product["name"] if target_product else "Samsung Galaxy S23 Ultra"
                v_desc = f"{target_variant.get('storage_capacity', '')} {target_variant.get('color', '')}".strip() if target_variant else "1 TB Phantom Black"
                v_price = target_variant.get("price_uzs", 17500000.0) if target_variant else 17500000.0
                price_str = f"{v_price:,.0f}".replace(",", " ")

                # 2.2 If phone number is provided, finalize and record the order!
                if phone_match:
                    phone_number = phone_match.group(1).replace(" ", "")
                    # Extract address: remove phone number and clean up
                    address_part = clean_text.replace(phone_match.group(0).lower(), "")
                    for marker in ["manzil:", "manzil", "adres:", "адрес:", "toshkent", "tashkent", "buyurtma", "bermoqchiman", "iltimos", "shahar", "tumani"]:
                        address_part = address_part.replace(marker, "")
                    address = address_part.strip(",. ") or "Toshkent shahri (kuryer qo'ng'iroq qilib aniqlaydi)"

                    v_id = target_variant.get("variant_id") if target_variant else None
                    order_res = await tool_create_order(
                        db=db,
                        business_id=business_id,
                        customer_id=customer_id,
                        shipping_address=address,
                        recipient_phone=phone_number,
                        product_variant_id=v_id,
                        product_id=target_product.get("product_id") if target_product else None,
                        quantity=1,
                        notes=f"Ordered via Telegram AI: {p_name} ({v_desc})",
                    )
                    tool_calls.append({"tool": "create_order", "result": order_res})

                    ord_num = order_res.get("order_number", "ORD-NEW")
                    ord_total = f"{order_res.get('total_amount_uzs', v_price):,.0f}".replace(",", " ")

                    order_confirmations = {
                        "uz": (
                            f"🎉 *Buyurtmangiz muvaffaqiyatli qabul qilindi!*\n\n"
                            f"📦 *Buyurtma raqami:* `{ord_num}`\n"
                            f"📱 *Mahsulot:* {p_name} ({v_desc})\n"
                            f"🔢 *Miqdori:* 1 dona\n"
                            f"💵 *Jami summa:* *{ord_total} UZS*\n"
                            f"📍 *Yetkazib berish manzili:* {address}\n"
                            f"📞 *Aloqa telefoni:* {phone_number}\n"
                            f"🚚 *Yetkazib berish:* 24 soat ichida Toshkent bo'ylab bepul\n\n"
                            f"🛡 *1 yillik rasmiy kafolat* va to'liq UzIMEI ro'yxatidan o'tgan.\n"
                            f"Operatorimiz 15 daqiqa ichida buyurtmani tasdiqlash uchun siz bilan bog'lanadi. "
                            f"Demo Electronics'ni tanlaganingiz uchun rahmat! 😊"
                        ),
                        "ru": (
                            f"🎉 *Ваш заказ успешно оформлен!*\n\n"
                            f"📦 *Номер заказа:* `{ord_num}`\n"
                            f"📱 *Товар:* {p_name} ({v_desc})\n"
                            f"🔢 *Количество:* 1 шт.\n"
                            f"💵 *Сумма к оплате:* *{ord_total} UZS*\n"
                            f"📍 *Адрес доставки:* {address}\n"
                            f"📞 *Контактный телефон:* {phone_number}\n"
                            f"🚚 *Доставка:* Бесплатно в течение 24 часов по Ташкенту\n\n"
                            f"🛡 *Официальная гарантия 1 год*, устройство зарегистрировано в UzIMEI.\n"
                            f"Наш оператор свяжется с вами в течение 15 минут для подтверждения отправки. "
                            f"Спасибо за покупку в Demo Electronics! 😊"
                        ),
                        "en": (
                            f"🎉 *Your order has been successfully placed!*\n\n"
                            f"📦 *Order Reference:* `{ord_num}`\n"
                            f"📱 *Product:* {p_name} ({v_desc})\n"
                            f"🔢 *Quantity:* 1 unit\n"
                            f"💵 *Total Amount:* *{ord_total} UZS*\n"
                            f"📍 *Shipping Address:* {address}\n"
                            f"📞 *Contact Phone:* {phone_number}\n"
                            f"🚚 *Delivery:* Free express delivery within 24 hours in Tashkent\n\n"
                            f"🛡 *1-Year Official Warranty* and official UzIMEI registration.\n"
                            f"Our support operator will contact you shortly to confirm fulfillment. "
                            f"Thank you for choosing Demo Electronics! 😊"
                        ),
                    }
                    return AIResponse(
                        text=order_confirmations.get(lang, order_confirmations["uz"]),
                        tool_calls_made=tool_calls,
                        escalated_to_human=False,
                        language_used=lang,
                        tokens_used=160,
                    )

                # 2.3 Customer wants to buy, but hasn't provided phone/address yet: Prompt politely!
                order_prompts = {
                    "uz": (
                        f"Ajoyib tanlov! *{p_name}* ({v_desc}) — *{price_str} UZS* uchun buyurtmani bajonidil rasmiylashtiraman! 😊\n\n"
                        f"Yetkazib berish xizmati Toshkent bo'ylab **bepul** amalga oshiriladi.\n\n"
                        f"Buyurtmani rasmiylashtirish uchun iltimos, quyidagilarni yuboring:\n"
                        f"1️⃣ **Telefon raqamingiz** (masalan: `+998 90 123 45 67`)\n"
                        f"2️⃣ **Yetkazib berish manzili** (shahar, tuman, ko'cha, uy)\n\n"
                        f"Yoki bir xabarda yozishingiz mumkin:\n"
                        f"«+998901234567, Toshkent, Chilonzor 5, 12-uy»"
                    ),
                    "ru": (
                        f"Отличный выбор! С удовольствием помогу оформить заказ на *{p_name}* ({v_desc}) — *{price_str} UZS*! 😊\n\n"
                        f"Доставка по Ташкенту бесплатная в течение 24 часов.\n\n"
                        f"Для оформления заказа отправьте, пожалуйста:\n"
                        f"1️⃣ **Номер телефона** (например: `+998 90 123 45 67`)\n"
                        f"2️⃣ **Адрес доставки** (район, улица, дом)\n\n"
                        f"Либо напишите одним сообщением:\n"
                        f"«+998901234567, Ташкент, Юнусабад 4, дом 10»"
                    ),
                    "en": (
                        f"Excellent choice! I would be glad to place your order for *{p_name}* ({v_desc}) — *{price_str} UZS*! 😊\n\n"
                        f"Delivery is **free** across Tashkent within 24 hours.\n\n"
                        f"To complete your order, please reply with:\n"
                        f"1️⃣ **Phone Number** (e.g. `+998 90 123 45 67`)\n"
                        f"2️⃣ **Delivery Address** (district, street, house number)\n\n"
                        f"Or send in a single line:\n"
                        f"«+998901234567, Tashkent, Mirzo Ulugbek, house 5»"
                    ),
                }
                return AIResponse(
                    text=order_prompts.get(lang, order_prompts["uz"]),
                    tool_calls_made=[],
                    escalated_to_human=False,
                    language_used=lang,
                    tokens_used=130,
                )

        # 3. Intent: Order Status Lookup
        order_match = re.search(r"\b(ORD-\d+(?:-\d+)?|[0-9]{4,8})\b", user_message, re.IGNORECASE)
        is_explicit_lookup = bool(order_match) or any(
            w in clean_text for w in ["buyurtmam", "buyurtma holati", "buyurtmani tekshirish", "status zakaza", "qayerda qoldi", "заказ где"]
        )
        if is_explicit_lookup:
            order_num = order_match.group(1).upper() if order_match else "ORD-1001"
            order_res = await tool_get_order_status(
                db=db,
                business_id=business_id,
                order_number=order_num,
                verified_customer_id=customer_id,
            )
            tool_calls.append({"tool": "get_order_status", "result": order_res})

            if "error" in order_res:
                replies = {
                    "uz": f"Kechirasiz, '{order_num}' raqamli buyurtma topilmadi yoki bu buyurtma sizning hisobingizga tegishli emas. Agar yangi buyurtma bermoqchi bo'lsangiz, bemalol yordam bera olaman!",
                    "ru": f"Заказ '{order_num}' не найден или не принадлежит вашему аккаунту. Если вы хотите сделать новый заказ, буду рад помочь!",
                    "en": f"Order '{order_num}' was not found or does not belong to your account. Feel free to ask if you would like to place a new order!",
                }
                return AIResponse(
                    text=replies.get(lang, replies["uz"]),
                    tool_calls_made=tool_calls,
                    escalated_to_human=False,
                    language_used=lang,
                    tokens_used=90,
                )
            else:
                formatted_amount = f"{order_res['total_amount_uzs']:,.0f}".replace(",", " ")
                replies = {
                    "uz": f"📦 *Buyurtma #{order_res['order_number']}*\nHolati: *{order_res['status'].upper()}*\nUmumiy summa: *{formatted_amount} UZS*\nManzil: {order_res.get('shipping_address') or 'Aniqlanmagan'}\nYetkazib berish bo'yicha kuryerimiz tez orada siz bilan bog'lanadi.",
                    "ru": f"📦 *Заказ #{order_res['order_number']}*\nСтатус: *{order_res['status'].upper()}*\nСумма: *{formatted_amount} UZS*\nАдрес: {order_res.get('shipping_address') or 'Уточняется'}",
                    "en": f"📦 *Order #{order_res['order_number']}*\nStatus: *{order_res['status'].upper()}*\nTotal: *{formatted_amount} UZS*",
                }
                return AIResponse(
                    text=replies.get(lang, replies["uz"]),
                    tool_calls_made=tool_calls,
                    escalated_to_human=False,
                    language_used=lang,
                    tokens_used=110,
                )

        # 4. Intent: Product Consultation & Recommendations (NEW)
        consult_keywords = [
            "maslahat", "tavsiya", "qaysi biri", "qaysi telefon", "qaysi noutbuk",
            "yaxshi telefon", "arzon telefon", "tavsiya eting", "maslahat bering", "tanlash",
            "посоветуйте", "что посоветуете", "какой телефон лучше", "какой ноутбук выбрать",
            "recommend", "which phone", "which laptop", "best phone", "advice"
        ]
        if any(w in clean_text for w in consult_keywords):
            consult_replies = {
                "uz": (
                    "Bajonidil maslahat beraman! Demo Electronics do'konida hozirda eng ommabop va sifatli modellar quyidagilar:\n\n"
                    "👑 *Eng zo'r flagmanlar (Kamera va O'yinlar uchun):*\n"
                    "• **Samsung Galaxy S24 Ultra / S23 Ultra** — 200MP kamera, 100x zoom, Snapdragon 8 Gen 2/3, o'rnatilgan S-Pen. (13 800 000 UZS dan)\n"
                    "• **Apple iPhone 16** — Yangi A18 protsessor, 48MP Fusion kamera, Camera Control tugmasi. (12 800 000 UZS dan)\n\n"
                    "💼 *O'qish, Dasturlash va Ish uchun noutbuk:*\n"
                    "• **Lenovo IdeaPad 3** — Intel Core i3 12-avlod, 8GB RAM, 512GB tezyurar SSD. (4 900 000 UZS)\n\n"
                    "💡 *Qulay va tejamkor smartfonlar:*\n"
                    "• **Xiaomi Redmi Note 13** — 108MP kamera, 120Hz AMOLED ekran. (2 100 000 UZS)\n"
                    "• **Samsung Galaxy A16** — 6.7 dyuymli AMOLED ekran, 50MP kamera. (2 450 000 UZS)\n\n"
                    "Siz uchun qaysi xususiyat eng muhim (kamera, batareya, o'yin yoki hamyonbop narx)? "
                    "Shunga qarab aynan sizga mos modelni tanlab beraman! 😊"
                ),
                "ru": (
                    "С удовольствием проконсультирую вас! В Demo Electronics представлены лучшие модели в каждой категории:\n\n"
                    "👑 *Топовые флагманы (Фото, Видео и Игры):*\n"
                    "• **Samsung Galaxy S24 Ultra / S23 Ultra** — Камера 200 Мп со 100x зумом, процессор Snapdragon 8 Gen 2/3, стилус S-Pen. (от 13 800 000 UZS)\n"
                    "• **Apple iPhone 16** — Новый чип A18, сенсорная кнопка Camera Control, 48 Мп Fusion камера. (от 12 800 000 UZS)\n\n"
                    "💼 *Для учебы, работы и программирования:*\n"
                    "• **Lenovo IdeaPad 3** — Intel Core i3 12-го поколения, 8 ГБ ОЗУ, 512 ГБ быстрый SSD. (4 900 000 UZS)\n\n"
                    "💡 *Надежный бюджетный сегмент:*\n"
                    "• **Xiaomi Redmi Note 13** — 108 Мп камера, плавный 120 Гц AMOLED экран. (2 100 000 UZS)\n"
                    "• **Samsung Galaxy A16** — 6.7'' яркий Super AMOLED экран, батарея 5000 мАч. (2 450 000 UZS)\n\n"
                    "Какой параметр для вас в приоритете — камера, производительность в играх или доступная цена? Буду рад помочь с выбором! 😊"
                ),
                "en": (
                    "I would be glad to give you tailored recommendations! Here are our top customer favorites:\n\n"
                    "👑 *Ultimate Flagships (Photography, Content & Gaming):*\n"
                    "• **Samsung Galaxy S23/S24 Ultra** — 200MP Quad Camera with 100x zoom, Snapdragon 8 Gen 2/3, S-Pen. (from 13,800,000 UZS)\n"
                    "• **Apple iPhone 16** — All-new A18 chip, Camera Control button, 48MP Fusion camera. (from 12,800,000 UZS)\n\n"
                    "💼 *Best Laptop for Studies & Professional Work:*\n"
                    "• **Lenovo IdeaPad 3** — Intel Core i3 12th Gen, 8GB RAM, 512GB NVMe SSD. (4,900,000 UZS)\n\n"
                    "💡 *Budget & Everyday Value:*\n"
                    "• **Xiaomi Redmi Note 13** — 108MP camera, 120Hz AMOLED. (2,100,000 UZS)\n"
                    "• **Samsung Galaxy A16** — 6.7\" AMOLED, 5000mAh battery. (2,450,000 UZS)\n\n"
                    "Which criteria matters most to you? Let me know and I will help you choose the ideal device! 😊"
                ),
            }
            return AIResponse(
                text=consult_replies.get(lang, consult_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=150,
            )

        # 5. Intent: Product Comparison (NEW)
        is_comparison = ("yoki" in clean_text or "vs" in clean_text or "или" in clean_text or "farqi" in clean_text or "сравнить" in clean_text) and (
            any(b in clean_text for b in ["iphone", "apple", "samsung", "s23", "s24", "a16", "redmi", "xiaomi", "lenovo"])
        )
        if is_comparison:
            comp_replies = {
                "uz": (
                    "Ajoyib savol! Ikkala model ham o'z yo'nalishida a'lo darajadagi qurilma:\n\n"
                    "🍎 **Apple iPhone 16:**\n"
                    "• Afzalliklari: iOS ekotizimi, A18 tezyurar chip, silliq video yozish sifati va Camera Control tugmasi.\n"
                    "• Narxi: *12 800 000 UZS* dan boshlanadi.\n\n"
                    "⚡️ **Samsung Galaxy S23 / S24 Ultra:**\n"
                    "• Afzalliklari: 200MP kamera va 100x Space Zoom, 6.8'' ulkan 120Hz Dynamic AMOLED ekran, o'rnatilgan S-Pen stilus va 5000 mA/soat sig'imli batareya.\n"
                    "• Narxi: *13 800 000 UZS* dan boshlanadi.\n\n"
                    "📌 **Xulosa:** Agar sizga iOS va uzoq muddatli barqarorlik kerak bo'lsa — iPhone 16; agar ulkan ekran, ko'p vazifalilik va maksimal zoom kamerasi muhim bo'lsa — Samsung Ultra eng to'g'ri tanlov!\n\n"
                    "Ulardan birortasini buyurtma qilishni xohlaysizmi?"
                ),
                "ru": (
                    "Отличное сравнение! Обе модели являются лидерами в своих категориях:\n\n"
                    "🍎 **Apple iPhone 16:**\n"
                    "• Плюсы: Экосистема Apple, мощный чип A18, великолепное качество видео и кнопка Camera Control.\n"
                    "• Цена: от *12 800 000 UZS*.\n\n"
                    "⚡️ **Samsung Galaxy S23 / S24 Ultra:**\n"
                    "• Плюсы: Камера 200 Мп с невероятным 100x зумом, большой 6.8'' 120 Гц AMOLED экран, перо S-Pen, батарея 5000 мАч.\n"
                    "• Цена: от *13 800 000 UZS*.\n\n"
                    "📌 **Итог:** Для съемки видео и экосистемы Apple выбирайте iPhone 16. Для максимальной функциональности, стилуса и фотосъемки с зумом — Samsung Ultra!\n\n"
                    "Хотите оформить заказ на какую-либо из этих моделей?"
                ),
                "en": (
                    "A great comparison! Both are premier devices for their respective ecosystems:\n\n"
                    "🍎 **Apple iPhone 16:**\n"
                    "• Highlights: Seamless iOS ecosystem, A18 processor, industry-best video recording, and Camera Control.\n"
                    "• Price: from *12,800,000 UZS*.\n\n"
                    "⚡️ **Samsung Galaxy S23/S24 Ultra:**\n"
                    "• Highlights: 200MP Quad Camera with 100x Zoom, 6.8'' 120Hz Dynamic AMOLED, integrated S-Pen, 5000mAh battery.\n"
                    "• Price: from *13,800,000 UZS*.\n\n"
                    "Would you like to order either model with free express delivery?"
                ),
            }
            return AIResponse(
                text=comp_replies.get(lang, comp_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=160,
            )

        # 6. Intent: Installment & Nasiya (Muddatli to'lov) (NEW)
        installment_keywords = ["nasiya", "muddatli", "bo'lib to'lash", "bolib tolash", "kredit", "rassrochka", "anorbank", "uzum nasiya", "zoodpay", "alif", "foizsiz", "рассрочка", "кредит", "в рассрочку", "installment"]
        if any(w in clean_text for w in installment_keywords):
            inst_replies = {
                "uz": (
                    "Ha, albatta! Demo Electronics do'konida barcha texnikalarni **muddatli to'lovga (nasiyaga)** xarid qilishingiz mumkin! 💳\n\n"
                    "📋 **Shartlarimiz:**\n"
                    "• Muddat: **3, 6 va 12 oyga**\n"
                    "• Boshlang'ich to'lov: **0% (boshlang'ich to'lovsiz)**\n"
                    "• Hamkorlar: **Anorbank, Uzum Nasiya, Alif Nasiya, Zoodpay**\n"
                    "• Kerakli hujjat: Faqat pasport yoki ID karta\n"
                    "• Tasdiqlash vaqti: Bor-yo'g'i 5-10 daqiqa!\n\n"
                    "Siz qaysi mahsulotni bo'lib to'lashga olmoqchisiz? Oylik to'lov summasini hisoblab berishim mumkin! 😊"
                ),
                "ru": (
                    "Да, конечно! В Demo Electronics доступна покупка любой техники в **выгодную рассрочку**! 💳\n\n"
                    "📋 **Условия оформления:**\n"
                    "• Срок: **3, 6 и 12 месяцев**\n"
                    "• Первоначальный взнос: **0%**\n"
                    "• Партнеры: **Anorbank, Uzum Nasiya, Alif Nasiya, Zoodpay**\n"
                    "• Документы: Только паспорт или ID-карта\n"
                    "• Одобрение: за 5-10 минут онлайн или в шоуруме!\n\n"
                    "Какую модель вы хотите оформить? Я могу рассчитать примерный ежемесячный платеж! 😊"
                ),
                "en": (
                    "Yes, absolutely! Demo Electronics offers flexible **0% down payment installment plans**! 💳\n\n"
                    "📋 **Terms:**\n"
                    "• Duration: **3, 6, or 12 months**\n"
                    "• Down payment: **0% required**\n"
                    "• Banking Partners: **Anorbank, Uzum Nasiya, Alif, Zoodpay**\n"
                    "• Required document: Passport or National ID card\n"
                    "• Instant approval within 5-10 minutes!\n\n"
                    "Which product would you like to calculate monthly installments for?"
                ),
            }
            return AIResponse(
                text=inst_replies.get(lang, inst_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=130,
            )

        # 7. Intent: Store Location & Showroom (NEW)
        location_keywords = ["manzil", "qayerda joylashgan", "dokon qayerda", "do'kon qayerda", "showroom", "moljal", "mo'ljal", "filial", "lokatsiya", "geolokatsiya", "адрес", "где находитесь", "локация", "где магазин", "address", "location", "where are you"]
        if any(w in clean_text for w in location_keywords):
            loc_replies = {
                "uz": (
                    "📍 *Demo Electronics do'koni va shourumi manzili:*\n\n"
                    "🏢 **Manzil:** Toshkent shahri, Yunusobod tumani, Amir Temur shoh ko'chasi, 107-uy.\n"
                    "🚇 **Mo'ljal:** Shahriston metro bekati yaqinida.\n"
                    "🕒 **Ish vaqti:** Dushanba – Shanba: 09:00 dan 20:00 gacha (Yakshanba: dam olish kuni).\n"
                    "📞 **Aloqa:** +998 71 200 00 00 | Telegram: @demoelectronics_support\n\n"
                    "Shourumimizga tashrif buyurib, qurilmalarni jonli ko'rishingiz va xarid qilishingiz mumkin! Sizni kutamiz! 😊"
                ),
                "ru": (
                    "📍 *Адрес шоурума Demo Electronics:*\n\n"
                    "🏢 **Адрес:** г. Ташкент, Юнусабадский район, проспект Амира Темура, дом 107.\n"
                    "🚇 **Ориентир:** рядом со станцией метро «Шахристан».\n"
                    "🕒 **Режим работы:** Понедельник – Суббота: с 09:00 до 20:00 (Воскресенье: выходной).\n"
                    "📞 **Телефон:** +998 71 200 00 00\n\n"
                    "Приходите в наш шоурум, чтобы лично протестировать технику перед покупкой!"
                ),
                "en": (
                    "📍 *Demo Electronics Showroom Location:*\n\n"
                    "🏢 **Address:** Tashkent, Yunusabad district, Amir Temur avenue, 107.\n"
                    "🚇 **Landmark:** Near Shahriston metro station.\n"
                    "🕒 **Working Hours:** Monday – Saturday: 09:00 to 20:00 (Sunday: Closed).\n"
                    "📞 **Phone:** +998 71 200 00 00\n\n"
                    "You are always welcome to visit our showroom and try out any device!"
                ),
            }
            return AIResponse(
                text=loc_replies.get(lang, loc_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=110,
            )

        # 8. Intent: Payment Methods (NEW)
        payment_keywords = ["to'lov", "qanday to'lash", "tolov", "click", "payme", "plastik", "naqd", "oplata", "kak platit", "оплата", "как оплатить", "payment", "how to pay"]
        if any(w in clean_text for w in payment_keywords) and not has_order_intent:
            pay_replies = {
                "uz": (
                    "💰 *Bizda barcha qulay to'lov turlari mavjud:*\n\n"
                    "1️⃣ **Elektron to'lovlar:** Click, Payme, Uzum Bank ilovalari orqali.\n"
                    "2️⃣ **Bank kartalari:** Uzcard, Humo, Visa va Mastercard.\n"
                    "3️⃣ **Naqd pul:** Kuryer buyurtmani yetkazib berganda tekshirib, joyida to'lashingiz mumkin.\n"
                    "4️⃣ **Muddatli to'lov (nasiya):** 3, 6 va 12 oyga foizsiz muddatli to'lov.\n\n"
                    "Siz qaysi to'lov usulidan foydalanmoqchisiz?"
                ),
                "ru": (
                    "💰 *У нас доступны все популярные и безопасные способы оплаты:*\n\n"
                    "1️⃣ **Онлайн-оплата:** Click, Payme, Uzum Bank.\n"
                    "2️⃣ **Банковские карты:** Uzcard, Humo, Visa, Mastercard.\n"
                    "3️⃣ **Оплата при получении:** Наличными или картой курьеру после проверки товара.\n"
                    "4️⃣ **Рассрочка:** На 3, 6 или 12 месяцев без первоначального взноса."
                ),
                "en": (
                    "💰 *We offer convenient payment methods:*\n\n"
                    "1️⃣ Digital payments: Click, Payme, Uzum Bank.\n"
                    "2️⃣ Credit & Debit cards: Uzcard, Humo, Visa, Mastercard.\n"
                    "3️⃣ Cash on delivery upon parcel inspection.\n"
                    "4️⃣ 0% down installment plans up to 12 months."
                ),
            }
            return AIResponse(
                text=pay_replies.get(lang, pay_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=110,
            )

        # 9. Intent: Product Authenticity & UzIMEI Guarantee (NEW)
        auth_keywords = ["original", "imei", "uzimei", "nusxami", "qalbaki", "poddelka", "оригинал", "оригинальный", "прошел imei", "genuine", "authentic"]
        if any(w in clean_text for w in auth_keywords):
            auth_replies = {
                "uz": (
                    "Ha, 100% kafolat beramiz! 🛡\n\n"
                    "• Bizdagi barcha texnikalar **100% original**, yangi va zavod qadog'ida (plomba bilan).\n"
                    "• Barcha smartfonlar O'zbekiston hududida to'liq **UzIMEI ro'yxatidan o'tgan** (ikkala SIM-karta uyasi ham faol).\n"
                    "• Har bir xarid uchun **1 yillik rasmiy servis kafolat taloni** taqdim etiladi.\n\n"
                    "Ko'nglingiz xotirjam bo'lishi mumkin! Xarid qilishni xohlaysizmi?"
                ),
                "ru": (
                    "Да, мы гарантируем 100% оригинальность! 🛡\n\n"
                    "• Вся продукция абсолютно новая, оригинальная и запечатанная в заводской упаковке.\n"
                    "• Все смартфоны официально **зарегистрированы в UzIMEI** (оба слота активны в Узбекистане).\n"
                    "• К каждому устройству прилагается **официальный гарантийный талон на 1 год**."
                ),
                "en": (
                    "Yes, guaranteed 100%! 🛡\n\n"
                    "• All our devices are genuine, brand-new, and sealed in original manufacturer packaging.\n"
                    "• Fully registered with **UzIMEI** for immediate cellular operation in Uzbekistan.\n"
                    "• Covered by a **1-year official warranty certificate**."
                ),
            }
            return AIResponse(
                text=auth_replies.get(lang, auth_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=110,
            )

        # 10. Intent: Store Identity & Capabilities (NEW)
        identity_keywords = ["siz kimsiz", "nima qila olasiz", "kim siz", "yordam ber", "qanday yordam", "kimsan", "кто вы", "что умеешь", "кто ты", "who are you", "what can you do"]
        if any(w in clean_text for w in identity_keywords):
            id_replies = {
                "uz": (
                    "Men **Demo Electronics** do'konining intellektual yordamchisiman! 🤖✨\n\n"
                    "Siz bilan xuddi do'kondagi mutaxassis kabi erkin suhbatlasha olaman. Menga quyidagi masalalarda murojaat qilishingiz mumkin:\n"
                    "1️⃣ **Mahsulot tanlash:** Har qanday telefon yoki noutbukning xususiyatlari va narxini bilish.\n"
                    "2️⃣ **Taqqoslash:** Ikki model o'rtasidagi farqni aniqlash (masalan: iPhone 16 yoki S23 Ultra).\n"
                    "3️⃣ **Buyurtma berish:** To'g'ridan-to'g'ri Telegram orqali xarid qilish.\n"
                    "4️⃣ **Kafolat va Yetkazib berish:** Yetkazish shartlari va do'konimiz manzili.\n\n"
                    "Sizga hozir qanday yordam bera olaman? 😊"
                ),
                "ru": (
                    "Я интеллектуальный консультант магазина **Demo Electronics**! 🤖✨\n\n"
                    "Я готов свободно общаться с вами и помогать по любым вопросам:\n"
                    "1️⃣ Подбор техники по параметрам и бюджету\n"
                    "2️⃣ Сравнение характеристик смартфонов и ноутбуков\n"
                    "3️⃣ Прямое оформление заказа с доставкой прямо в чате\n"
                    "4️⃣ Консультация по гарантии, рассрочке и адресам\n\n"
                    "Чем я могу помочь вам прямо сейчас? 😊"
                ),
                "en": (
                    "I am the intelligent virtual advisor for **Demo Electronics**! 🤖✨\n\n"
                    "I can chat with you freely just like an in-store specialist:\n"
                    "1️⃣ Discover specs, prices, and stock for any smartphone or laptop\n"
                    "2️⃣ Compare models side by side (e.g. iPhone 16 vs Galaxy S23 Ultra)\n"
                    "3️⃣ Place an order directly here in Telegram\n"
                    "4️⃣ Assist with warranty, installments, and delivery inquiries\n\n"
                    "How can I help you today? 😊"
                ),
            }
            return AIResponse(
                text=id_replies.get(lang, id_replies["uz"]),
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=120,
            )

        # 11. Intent: Delivery Policy
        if any(w in clean_text for w in ["yetkazib", "dostavka", "доставка", "delivery", "dastavka", "kuryer", "курьер"]):
            del_res = await tool_get_delivery_policy(db=db, business_id=business_id)
            tool_calls.append({"tool": "get_delivery_policy", "result": del_res})

            policy_text = ""
            for p in del_res.get("policies", []):
                if p["language"] == lang:
                    policy_text = p["policy"]
                    break
            if not policy_text and del_res.get("policies"):
                policy_text = del_res["policies"][0]["policy"]

            header = "🚚 *Yetkazib berish shartlari:*" if lang == "uz" else ("🚚 *Условия доставки:*" if lang == "ru" else "🚚 *Delivery Information:*")
            return AIResponse(
                text=f"{header}\n\n{policy_text}\n\nBuyurtma berishni xohlaysizmi? Yetkazib berish manzilini yuboring va biz tezda jo'natamiz! 😊",
                tool_calls_made=tool_calls,
                escalated_to_human=False,
                language_used=lang,
                tokens_used=140,
            )

        # 12. Intent: Return & Warranty Policy
        if any(w in clean_text for w in ["kafolat", "qaytarish", "almashtirish", "гарантия", "возврат", "обмен", "warranty", "return"]):
            ret_res = await tool_get_return_policy(db=db, business_id=business_id)
            tool_calls.append({"tool": "get_return_policy", "result": ret_res})

            policy_text = ""
            for p in ret_res.get("policies", []):
                if p["language"] == lang:
                    policy_text = p["policy"]
                    break
            if not policy_text and ret_res.get("policies"):
                policy_text = ret_res["policies"][0]["policy"]

            header = "🛡 *Kafolat va qaytarish:* " if lang == "uz" else ("🛡 *Гарантия и возврат:*" if lang == "ru" else "🛡 *Warranty and Returns:*")
            return AIResponse(
                text=f"{header}\n\n{policy_text}",
                tool_calls_made=tool_calls,
                escalated_to_human=False,
                language_used=lang,
                tokens_used=130,
            )

        # 13. Intent: Business Hours
        if any(w in clean_text for w in ["ish vaqti", "qachongacha", "ochiq", "часы работы", "режим работы", "working hours", "open"]):
            hours_res = await tool_get_business_hours(db=db, business_id=business_id)
            tool_calls.append({"tool": "get_business_hours", "result": hours_res})

            b_name = hours_res.get("business_name", "Demo Electronics")
            hours = hours_res.get("working_hours", {})
            schedule = "\n".join(f"• {k.replace('_', ' ').capitalize()}: {v}" for k, v in hours.items())
            header = f"🕒 *{b_name} ish vaqti:*" if lang == "uz" else f"🕒 *Часы работы {b_name}:*"
            return AIResponse(
                text=f"{header}\n{schedule}\n\nShourumimizga tashrif buyuring yoki onlayn buyurtma bering! 😊",
                tool_calls_made=tool_calls,
                escalated_to_human=False,
                language_used=lang,
                tokens_used=100,
            )

        # 14. Intent: Product / Catalog / Price Search
        search_query = clean_text
        elliptical_keywords = {"128", "256", "512", "64", "gb", "ssd", "ram", "rangi", "ranglari", "narxi", "qancha", "turadi", "bormi", "color", "colors", "price", "black", "blue", "white", "grey", "mavjudmi"}
        query_words = set(re.findall(r"[a-zA-Z0-9]+", clean_text))
        stopwords = {"bormi", "va", "qancha", "the", "what", "is", "how", "much", "narxi", "turadi", "haqida"}
        meaningful_words = query_words - stopwords

        if history and meaningful_words and meaningful_words.issubset(elliptical_keywords):
            for past_turn in reversed(history):
                content = past_turn.get("content", "").lower()
                for known_brand in ["samsung", "apple", "iphone", "xiaomi", "lenovo", "redmi"]:
                    if known_brand in content:
                        search_query = f"{known_brand} {clean_text}"
                        break
                if search_query != clean_text:
                    break

        search_res = await tool_search_products(db=db, business_id=business_id, query=search_query)
        tool_calls.append({"tool": "search_products", "result": search_res})

        products = search_res.get("products", [])
        if products:
            p = products[0]
            variants = p.get("variants", [])
            lines = []

            if lang == "uz":
                lines.append(f"Assalomu alaykum! Hurmatli mijoz, siz so'ragan *{p['name']}* bo'yicha ma'lumotlar bilan bajonidil tanishtiraman:\n")
                lines.append(f"📱 *{p['name']}* ({p['brand']})")
                if p.get('description'):
                    lines.append(f"_{p['description']}_\n")
                if variants:
                    lines.append("💰 *Mavjud modellar va narxlar:*")
                    for v in variants:
                        price_formatted = f"{v['price_uzs']:,.0f}".replace(",", " ")
                        stock_txt = "✅ Omborda mavjud" if v["stock_quantity"] > 0 else "⏳ Hozirda qolmagan"
                        lines.append(f"• *{v['storage_capacity'] or ''}* {v['color'] or ''} ({v['sku']}): *{price_formatted} UZS* ({stock_txt})")
                else:
                    lines.append("Ushbu mahsulot narxi hozirda tasdiqlanmagan.")

                lines.append(
                    "\n✨ *Demo Electronics afzalliklari:*\n"
                    "🛡 1 yillik rasmiy kafolat\n"
                    "🚚 Toshkent bo'ylab 24 soat ichida bepul yetkazib berish\n"
                    "💳 Click, Payme yoki muddatli to'lov (bo'lib to'lash)\n\n"
                    "Ushbu modelni buyurtma qilishni xohlaysizmi? Telefon raqamingiz va manzilingizni yozsangiz, darhol rasmiylashtirib beraman! 😊"
                )
            elif lang == "ru":
                lines.append(f"Здравствуйте! Уважаемый клиент, с удовольствием предоставлю информацию по интересующей вас модели *{p['name']}*:\n")
                lines.append(f"📱 *{p['name']}* ({p['brand']})")
                if p.get('description'):
                    lines.append(f"_{p['description']}_\n")
                if variants:
                    lines.append("💰 *Доступные комплектации и цены:*")
                    for v in variants:
                        price_formatted = f"{v['price_uzs']:,.0f}".replace(",", " ")
                        stock_txt = "✅ В наличии" if v["stock_quantity"] > 0 else "⏳ Нет в наличии"
                        lines.append(f"• *{v['storage_capacity'] or ''}* {v['color'] or ''} ({v['sku']}): *{price_formatted} UZS* ({stock_txt})")
                else:
                    lines.append("Цена на данный товар не подтверждена.")

                lines.append(
                    "\n✨ *Преимущества покупки в Demo Electronics:*\n"
                    "🛡 Официальная сервисная гарантия 1 год\n"
                    "🚚 Быстрая бесплатная доставка по Ташкенту\n"
                    "💳 Оплата картой, наличными или в рассрочку\n\n"
                    "Желаете оформить заказ? Отправьте ваш телефон и адрес, и я сразу зафиксирую заявку! 😊"
                )
            else:
                lines.append(f"Hello! Dear customer, I would be delighted to provide details regarding the *{p['name']}*:\n")
                lines.append(f"📱 *{p['name']}* ({p['brand']})")
                if p.get('description'):
                    lines.append(f"_{p['description']}_\n")
                if variants:
                    lines.append("💰 *Available Configurations & Verified Prices:*")
                    for v in variants:
                        price_formatted = f"{v['price_uzs']:,.0f}".replace(",", " ")
                        stock_txt = "✅ In Stock" if v["stock_quantity"] > 0 else "⏳ Out of Stock"
                        lines.append(f"• *{v['storage_capacity'] or ''}* {v['color'] or ''} ({v['sku']}): *{price_formatted} UZS* ({stock_txt})")
                else:
                    lines.append("Verified pricing is currently unavailable for this item.")

                lines.append(
                    "\n✨ *Demo Electronics Store Advantages:*\n"
                    "🛡 1-year official manufacturer warranty\n"
                    "🚚 Free express delivery within 24 hours across Tashkent\n"
                    "💳 Credit cards, bank transfers, and installment options accepted\n\n"
                    "Would you like to place an order? Simply reply with your contact number and delivery address! 😊"
                )

            return AIResponse(
                text="\n".join(lines),
                tool_calls_made=tool_calls,
                escalated_to_human=False,
                language_used=lang,
                tokens_used=180,
            )

        # 15. Unverified / Unknown Product or Question
        unconfirmed_replies = {
            "uz": (
                f"Assalomu alaykum! Hurmatli mijoz, afsuski, «*{user_message}*» bo'yicha ma'lumotlar bazamizda tasdiqlangan narx yoki mahsulot topilmadi.\n\n"
                "Do'konimizda boshqa ommabop flagman modellar (Samsung Galaxy S23/S24 Ultra, Apple iPhone 16, Xiaomi Redmi) rasmiy kafolat bilan mavjud.\n"
                "Sizga kerakli mahsulotni tanlashda yordam berishimni yoki do'kon operatorimiz bilan bog'lashimizni xohlaysizmi?"
            ),
            "ru": (
                f"Здравствуйте! Уважаемый клиент, к сожалению, по вашему запросу «*{user_message}*» в нашем каталоге не найдено подтвержденных товаров или цен.\n\n"
                "В нашем магазине доступны популярные флагманские модели Samsung, Apple iPhone и Xiaomi с официальной гарантией.\n"
                "Желаете, я переведу диалог на оператора поддержки или помогу подобрать похожий товар?"
            ),
            "en": (
                f"Hello! Dear customer, I could not find verified pricing or product details for \"*{user_message}*\" in our active catalog.\n\n"
                "We do carry popular models from Samsung, Apple iPhone, and Xiaomi with official 1-year warranties.\n"
                "Would you like me to connect you with our customer support operator or suggest an alternative?"
            ),
        }
        return AIResponse(
            text=unconfirmed_replies.get(lang, unconfirmed_replies["uz"]),
            tool_calls_made=tool_calls,
            escalated_to_human=False,
            language_used=lang,
            tokens_used=110,
        )
