"""Internationalization (i18n) dictionary and locale helper."""

from typing import Dict, Any

MESSAGES: Dict[str, Dict[str, str]] = {
    "uz": {
        "welcome": (
            "👋 *NEXUS AI qo'llab-quvvatlash tizimiga xush kelibsiz!*\n\n"
            "Assalomu alaykum! Men *{business_name}* do'konining aqlli yordamchisiman.\n\n"
            "Men quyidagi masalalarda yordam bera olaman:\n"
            "• Mahsulotlar va narxlar\n"
            "• Ombordagi qoldiqlar\n"
            "• Buyurtma holatini tekshirish\n"
            "• Yetkazib berish va to'lov shartlari\n"
            "• Kafolat va tovarni qaytarish\n"
            "• Jonli operator bilan bog'lanish\n\n"
            "Quyidagi menyudan kerakli bo'limni tanlang yoki savolingizni to'g'ridan-to'g'ri yozing:"
        ),
        "choose_language": "Iltimos, muloqot tilini tanlang:\nПожалуйста, выберите язык:\nPlease select your language:",
        "language_updated": "✅ Muloqot tili o'zbek tiliga o'zgartirildi.",
        "menu_products": "📱 Mahsulotlar",
        "menu_search": "🔍 Qidiruv",
        "menu_orders": "📦 Buyurtmalarim",
        "menu_delivery": "🚚 Yetkazib berish",
        "menu_warranty": "🛡 Qaytarish va kafolat",
        "menu_faq": "❓ Ko'p beriladigan savollar",
        "menu_support": "👨‍💼 Operator bilan bog'lanish",
        "menu_language": "🌐 Tilni o'zgartirish",
        "back_to_menu": "⬅️ Bosh menyu",
        "help_text": (
            "ℹ️ *NEXUS AI Botidan foydalanish bo'yicha qo'llanma*\n\n"
            "Siz tugmalardan foydalanishingiz yoki o'zingizni qiziqtirgan savolni oddiy so'zlar bilan yozishingiz mumkin.\n\n"
            "Misollar:\n"
            "• \"Samsung A16 128 GB narxi qancha?\"\n"
            "• \"Toshkentga yetkazib berish qancha turadi?\"\n"
            "• \"Menga operator kerak\"\n\n"
            "Asosiy buyruqlar:\n"
            "/start - Botni qayta ishga tushirish\n"
            "/help - Qo'llanmani ko'rish\n"
            "/menu - Asosiy menyuni ochish"
        ),
        "ask_search_query": "Qidirayotgan mahsulot nomini yozing (masalan: *Samsung A16* yoki *iPhone*):",
        "ask_order_number": "Iltimos, buyurtma raqamingizni kiriting (masalan: *ORD-1001*):",
        "operator_requested": (
            "👨‍💼 *So'rovingiz operatorga yo'naltirildi!*\n\n"
            "Tez orada qo'llab-quvvatlash xizmati mutaxassisi siz bilan ushbu chat orqali bog'lanadi. "
            "Iltimos, kuting."
        ),
        "operator_already_active": "Siz hozirda mutaxassis bilan bog'langansiz. Savollaringizni to'g'ridan-to'g'ri yozishingiz mumkin.",
        "order_not_found": "Kechirasiz, ushbu raqamli buyurtma topilmadi yoki bu buyurtma sizning hisobingizga tegishli emas.",
        "no_products_found": "Kechirasiz, so'rovingiz bo'yicha mahsulot topilmadi.",
        "error_generic": "Texnik xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring.",
    },
    "ru": {
        "welcome": (
            "👋 *Добро пожаловать в службу поддержки NEXUS AI!*\n\n"
            "Здравствуйте! Я виртуальный консультант магазина *{business_name}*.\n\n"
            "Я могу помочь вам со следующими вопросами:\n"
            "• Информация о товарах и ценах\n"
            "• Наличие на складе\n"
            "• Проверка статуса заказа\n"
            "• Условия и стоимость доставки\n"
            "• Гарантия и возврат товара\n"
            "• Связь с оператором\n\n"
            "Выберите нужный раздел в меню ниже или просто напишите свой вопрос:"
        ),
        "choose_language": "Пожалуйста, выберите язык общения:\nIltimos, muloqot tilini tanlang:\nPlease select your language:",
        "language_updated": "✅ Язык общения изменен на русский.",
        "menu_products": "📱 Продукты",
        "menu_search": "🔍 Поиск товаров",
        "menu_orders": "📦 Мои заказы",
        "menu_delivery": "🚚 Доставка",
        "menu_warranty": "🛡 Возврат и гарантия",
        "menu_faq": "❓ Частые вопросы (FAQ)",
        "menu_support": "👨‍💼 Связаться с оператором",
        "menu_language": "🌐 Изменить язык",
        "back_to_menu": "⬅️ Главное меню",
        "help_text": (
            "ℹ️ *Справка по использованию NEXUS AI*\n\n"
            "Вы можете нажимать кнопки меню или задавать любые вопросы обычным текстом.\n\n"
            "Примеры вопросов:\n"
            "• \"Сколько стоит Samsung A16 128 GB?\"\n"
            "• \"Каковы условия доставки по Ташкенту?\"\n"
            "• \"Соедините меня с оператором\"\n\n"
            "Команды:\n"
            "/start - Перезапуск бота\n"
            "/help - Справка\n"
            "/menu - Главное меню"
        ),
        "ask_search_query": "Введите название товара для поиска (например: *Samsung A16* или *iPhone*):",
        "ask_order_number": "Пожалуйста, укажите номер вашего заказа (например: *ORD-1001*):",
        "operator_requested": (
            "👨‍💼 *Ваш запрос передан оператору!*\n\n"
            "Специалист службы поддержки ответит вам прямо в этом чате в ближайшее время."
        ),
        "operator_already_active": "Диалог переведен на оператора. Ожидайте ответа специалиста.",
        "order_not_found": "Заказ с таким номером не найден или не принадлежит вашему аккаунту.",
        "no_products_found": "К сожалению, по вашему запросу товары не найдены.",
        "error_generic": "Произошла временная ошибка. Пожалуйста, попробуйте позже.",
    },
    "en": {
        "welcome": (
            "👋 *Welcome to NEXUS AI Support!*\n\n"
            "Hello! I am the virtual assistant for *{business_name}*.\n\n"
            "I can assist you with:\n"
            "• Product information and verified prices\n"
            "• Real-time stock availability\n"
            "• Order tracking\n"
            "• Delivery rates and policies\n"
            "• Returns and warranties\n"
            "• Live human operator assistance\n\n"
            "Select an option from the menu below or simply type your question:"
        ),
        "choose_language": "Please select your preferred language:\nIltimos, tilni tanlang:\nПожалуйста, выберите язык:",
        "language_updated": "✅ Language updated to English.",
        "menu_products": "📱 Products",
        "menu_search": "🔍 Search Catalog",
        "menu_orders": "📦 My Orders",
        "menu_delivery": "🚚 Delivery Info",
        "menu_warranty": "🛡 Returns & Warranty",
        "menu_faq": "❓ FAQ",
        "menu_support": "👨‍💼 Contact Support",
        "menu_language": "🌐 Language Settings",
        "back_to_menu": "⬅️ Main Menu",
        "help_text": (
            "ℹ️ *NEXUS AI Bot Guide*\n\n"
            "You can navigate using the buttons below or ask questions in natural language.\n\n"
            "Examples:\n"
            "• \"How much is the Samsung A16 128 GB?\"\n"
            "• \"What are your delivery fees to Samarkand?\"\n"
            "• \"I need to speak with a human\"\n\n"
            "Commands:\n"
            "/start - Start or restart the bot\n"
            "/help - Help & instructions\n"
            "/menu - Open main menu"
        ),
        "ask_search_query": "Please enter the product name you are looking for (e.g., *Samsung A16* or *iPhone*):",
        "ask_order_number": "Please enter your order number (e.g., *ORD-1001*):",
        "operator_requested": (
            "👨‍💼 *Your request has been forwarded to a support representative!*\n\n"
            "An agent will review your inquiry and reply in this chat shortly."
        ),
        "operator_already_active": "You are currently connected to an operator. Please wait for their response.",
        "order_not_found": "We could not find an order matching that identifier for your account.",
        "no_products_found": "No products matched your search criteria.",
        "error_generic": "A temporary error occurred. Please try again shortly.",
    },
    "uz_cyrl": {
        "welcome": (
            "👋 *NEXUS AI қўллаб-қувватлаш тизимига хуш келибсиз!*\n\n"
            "Ассалому алайкум! Мен *{business_name}* дўконининг ақлли ёрдамчисиман.\n\n"
            "Мен қуйидаги масалаларда ёрдам бера оламан:\n"
            "• Маҳсулотлар ва нархлар\n"
            "• Омбордаги қолдиқлар\n"
            "• Буюртма ҳолатини текшириш\n"
            "• Етказиб бериш ва тўлов шартлари\n"
            "• Кафолат ва товарни қайтариш\n"
            "• Жонли оператор билан боғланиш\n\n"
            "Қуйидаги менюдан керакли бўлимни танланг ёки саволингизни тўғридан-тўғри ёзинг:"
        ),
        "choose_language": "Илтимос, мулоқот тилини танланг:\nПожалуйста, выберите язык:\nPlease select your language:",
        "language_updated": "✅ Мулоқот тили ўзбекчага (кирилл) ўзгартирилди.",
        "menu_products": "📱 Маҳсулотлар",
        "menu_search": "🔍 Қидирув",
        "menu_orders": "📦 Буюртмаларим",
        "menu_delivery": "🚚 Етказиб бериш",
        "menu_warranty": "🛡 Қайтариш ва кафолат",
        "menu_faq": "❓ Кўп бериладиган саволлар",
        "menu_support": "👨‍💼 Оператор билан боғланиш",
        "menu_language": "🌐 Тилни ўзгартириш",
        "back_to_menu": "⬅️ Бош меню",
        "help_text": (
            "ℹ️ *NEXUS AI Ботидан фойдаланиш бўйича қўлланма*\n\n"
            "Сиз тугмалардан фойдаланишингиз ёки саволингизни оддий сўзлар билан ёзишингиз мумкин."
        ),
        "ask_search_query": "Қидираётган маҳсулот номини ёзинг:",
        "ask_order_number": "Илтимос, буюртма рақамингизни киритинг:",
        "operator_requested": "👨‍💼 *Сўровингиз операторга йўналтирилди!* Тез орада мутахассис боғланади.",
        "operator_already_active": "Сиз ҳозирда мутахассис билан боғлангансиз.",
        "order_not_found": "Буюртма топилмади.",
        "no_products_found": "Маҳсулот топилмади.",
        "error_generic": "Техник хатолик юз берди.",
    },
}


def get_text(key: str, lang: str = "uz", **kwargs: Any) -> str:
    """Retrieve localized message string with fallback to Uzbek then English."""
    lang_dict = MESSAGES.get(lang, MESSAGES.get("uz", {}))
    msg = lang_dict.get(key) or MESSAGES.get("uz", {}).get(key) or MESSAGES.get("en", {}).get(key, key)
    if kwargs:
        try:
            return msg.format(**kwargs)
        except KeyError:
            return msg
    return msg
