"""Zero-dependency Offline Mock AI Engine for testing and local execution."""

import re
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.ai.schemas import AIResponse
from backend.app.ai.tools import (
    tool_check_inventory,
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
    """Deterministic intent-matching AI engine executing identical database tools."""

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
        """Process customer query using deterministic tool dispatch."""
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
                    "Bizda smartfonlar (Samsung, Apple iPhone, Xiaomi), noutbuklar va aksessuarlarning eng so'nggi modellari, "
                    "rasmiy kafolat va Toshkent bo'ylab bepul tezkor yetkazib berish xizmati mavjud.\n\n"
                    "Bugun sizga qaysi mahsulot yoki xizmatimiz bo'yicha ma'lumot berishim mumkin?"
                ),
                "ru": (
                    "Здравствуйте! Добро пожаловать в службу заботы о клиентах Demo Electronics! 😊\n\n"
                    "Мы рады предложить вам оригинальную технику Samsung, Apple, Xiaomi, ноутбуки Lenovo, "
                    "официальную гарантию 1 год и бесплатную доставку по Ташкенту.\n\n"
                    "Какая модель или вопрос вас интересует сегодня?"
                ),
                "en": (
                    "Hello! Welcome to Demo Electronics intelligent customer support! 😊\n\n"
                    "We are happy to assist you with the latest smartphones (Samsung, Apple iPhone, Xiaomi), laptops, "
                    "official 1-year warranties, and fast free delivery across Tashkent.\n\n"
                    "How may I assist you with our catalog or services today?"
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
            # Trigger ticket creation
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

        # 2. Intent: Order Status Lookup
        order_match = re.search(r"\b(ORD-\d+|[0-9]{4,8})\b", user_message, re.IGNORECASE)
        if order_match or any(w in clean_text for w in ["buyurtma", "buyurtmam", "zakaz", "заказ", "order", "my order"]):
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
                    "uz": f"Kechirasiz, '{order_num}' raqamli buyurtma topilmadi yoki bu buyurtma sizning hisobingizga tegishli emas.",
                    "ru": f"Заказ '{order_num}' не найден или не принадлежит вашему аккаунту.",
                    "en": f"Order '{order_num}' was not found or does not belong to your account.",
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
                    "uz": f"📦 *Buyurtma #{order_res['order_number']}*\nHolati: *{order_res['status']}*\nUmumiy summa: *{formatted_amount} UZS*",
                    "ru": f"📦 *Заказ #{order_res['order_number']}*\nСтатус: *{order_res['status']}*\nСумма: *{formatted_amount} UZS*",
                    "en": f"📦 *Order #{order_res['order_number']}*\nStatus: *{order_res['status']}*\nTotal: *{formatted_amount} UZS*",
                }
                return AIResponse(
                    text=replies.get(lang, replies["uz"]),
                    tool_calls_made=tool_calls,
                    escalated_to_human=False,
                    language_used=lang,
                    tokens_used=110,
                )

        # 3. Intent: Delivery Policy
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
                text=f"{header}\n\n{policy_text}",
                tool_calls_made=tool_calls,
                escalated_to_human=False,
                language_used=lang,
                tokens_used=140,
            )

        # 4. Intent: Return & Warranty Policy
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

        # 5. Intent: Business Hours
        if any(w in clean_text for w in ["ish vaqti", "qachongacha", "ochiq", "часы работы", "режим работы", "working hours", "open"]):
            hours_res = await tool_get_business_hours(db=db, business_id=business_id)
            tool_calls.append({"tool": "get_business_hours", "result": hours_res})

            b_name = hours_res.get("business_name", "Do'kon")
            hours = hours_res.get("working_hours", {})
            schedule = "\n".join(f"• {k.replace('_', ' ').capitalize()}: {v}" for k, v in hours.items())
            header = f"🕒 *{b_name} ish vaqti:*" if lang == "uz" else f"🕒 *Часы работы {b_name}:*"
            return AIResponse(
                text=f"{header}\n{schedule}",
                tool_calls_made=tool_calls,
                escalated_to_human=False,
                language_used=lang,
                tokens_used=100,
            )

        # 6. Intent: Product / Catalog / Price Search
        # Inherit brand from history only for elliptical follow-ups (e.g. "128 GB qancha?", "ranglari qanaqa?")
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

            # Courteous, respectful human-like opening
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
                    "Ushbu modelni buyurtma qilishni xohlaysizmi yoki operatorimiz yordami kerakmi? Sizga xizmat qilishdan xursandman! 😊"
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
                    "Хотите оформить заказ или связаться с нашим оператором? Буду рад помочь вам! 😊"
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
                    "Would you like to place an order or connect with our customer support operator? Happy to assist! 😊"
                )

            return AIResponse(
                text="\n".join(lines),
                tool_calls_made=tool_calls,
                escalated_to_human=False,
                language_used=lang,
                tokens_used=180,
            )

        # 7. Unverified / Unknown Product or Question
        unconfirmed_replies = {
            "uz": (
                f"Assalomu alaykum! Hurmatli mijoz, afsuski, «*{user_message}*» bo'yicha ma'lumotlar bazamizda tasdiqlangan narx yoki mahsulot topilmadi.\n\n"
                "Do'konimizda boshqa ommabop flagman modellar (Samsung Galaxy, Apple iPhone, Xiaomi) rasmiy kafolat bilan mavjud.\n"
                "Sizga kerakli mahsulotni aniqlash yoki buyurtma asosida olib kelish uchun do'kon operatorimiz bilan bog'lashimizni xohlaysizmi?"
            ),
            "ru": (
                f"Здравствуйте! Уважаемый клиент, к сожалению, по вашему запросу «*{user_message}*» в нашем каталоге не найдено подтвержденных товаров или цен.\n\n"
                "В нашем магазине доступны другие популярные флагманские модели Samsung, Apple iPhone и Xiaomi с официальной гарантией.\n"
                "Желаете, я переведу диалог на оператора поддержки, чтобы мы помогли подобрать товар или оформить индивидуальный заказ?"
            ),
            "en": (
                f"Hello! Dear customer, I could not find verified pricing or product details for \"*{user_message}*\" in our active catalog.\n\n"
                "We do carry popular flagship models from Samsung, Apple iPhone, and Xiaomi with official 1-year warranties.\n"
                "Would you like me to connect you with our customer support operator to assist you further?"
            ),
        }
        return AIResponse(
            text=unconfirmed_replies.get(lang, unconfirmed_replies["uz"]),
            tool_calls_made=tool_calls,
            escalated_to_human=False,
            language_used=lang,
            tokens_used=110,
        )
