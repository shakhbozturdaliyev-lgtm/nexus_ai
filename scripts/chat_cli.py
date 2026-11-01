"""Interactive CLI console to converse directly with the NEXUS AI agent."""

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.ai.orchestrator import orchestrator
from backend.app.bot.session import get_or_create_active_conversation, get_or_create_customer
from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal
from backend.app.database.seed import seed_data


async def interactive_chat():
    print("=" * 70)
    print("🚀 NEXUS AI — Interactive Customer Support Console")
    print("=" * 70)
    print(f"Business: Demo Electronics (ID: {settings.default_business_id})")
    print(f"Timezone: {settings.default_timezone} | Currency: {settings.default_currency}")
    print(f"AI Mode: {'Gemini Live' if settings.gemini_api_key and not settings.ai_mock_mode else 'Offline Mock Engine (Deterministic)'}")
    print("Commands: ':lang uz', ':lang ru', ':lang en', ':exit'")
    print("=" * 70)

    # Ensure DB is seeded
    await seed_data()

    telegram_id = 998901234
    current_lang = "uz"

    async with AsyncSessionLocal() as db:
        customer = await get_or_create_customer(
            db, telegram_user_id=telegram_id, display_name="Console Customer", language_code=current_lang
        )
        conversation = await get_or_create_active_conversation(db, customer.id)
        await db.commit()

        print(f"\nConnected Customer: {customer.display_name} (Lang: {current_lang})")
        print("Type your message or test queries below.\n")

        # If custom command-line arguments are passed, process them
        if len(sys.argv) > 1:
            # Allow optional --lang flag: python scripts/chat_cli.py --lang ru "Сколько стоит доставка?"
            lang = current_lang
            args = sys.argv[1:]
            if args[0] in ["--lang", "-l"] and len(args) > 2:
                lang = args[1]
                query = " ".join(args[2:])
            else:
                query = " ".join(args)

            print(f"👤 Customer [{lang}]: {query}")
            response = await orchestrator.process_message(
                db=db,
                business_id=settings.default_business_id,
                customer_id=customer.id,
                conversation_id=conversation.id,
                user_message=query,
                lang=lang,
            )
            print(f"🤖 NEXUS AI:\n{response.text}")
            if response.tool_calls_made:
                tools = [tc["tool"] for tc in response.tool_calls_made]
                print(f"   [Tools executed: {', '.join(tools)}]")
            if response.escalated_to_human:
                print("   ⚠️ [Escalated to human operator]")
            return

        # Interactive loop if TTY, or automated demo queries if non-interactive
        if not sys.stdin.isatty():
            # Run demonstration queries
            demo_queries = [
                ("uz", "Assalomu alaykum! Samsung Galaxy A16 narxi qancha va sotuvda bormi?"),
                ("uz", "Toshkent shahri bo'ylab yetkazib berish qancha turadi?"),
                ("ru", "Сколько стоит доставка в Самарканд?"),
                ("uz", "Menga inson kerak, operator bilan bog'lang"),
                ("en", "Do you have PlayStation 6 and what is the price?"),
            ]
            for lang, query in demo_queries:
                print(f"\n👤 Customer [{lang}]: {query}")
                response = await orchestrator.process_message(
                    db=db,
                    business_id=settings.default_business_id,
                    customer_id=customer.id,
                    conversation_id=conversation.id,
                    user_message=query,
                    lang=lang,
                )
                print(f"🤖 NEXUS AI:\n{response.text}")
                if response.tool_calls_made:
                    tools = [tc["tool"] for tc in response.tool_calls_made]
                    print(f"   [Tools executed: {', '.join(tools)}]")
                if response.escalated_to_human:
                    print("   ⚠️ [Escalated to human operator]")
            return

        while True:
            try:
                user_input = input(f"\n[{current_lang}] Customer > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting session...")
                break

            if not user_input:
                continue
            if user_input.lower() in [":exit", "exit", "quit"]:
                print("Session terminated.")
                break
            if user_input.startswith(":lang"):
                parts = user_input.split()
                if len(parts) > 1 and parts[1] in ["uz", "ru", "en", "uz_cyrl"]:
                    current_lang = parts[1]
                    print(f"Language switched to: {current_lang}")
                    continue
                else:
                    print("Usage: :lang uz | :lang ru | :lang en")
                    continue

            # Process with AI Orchestrator
            response = await orchestrator.process_message(
                db=db,
                business_id=settings.default_business_id,
                customer_id=customer.id,
                conversation_id=conversation.id,
                user_message=user_input,
                lang=current_lang,
            )

            print(f"\n🤖 NEXUS AI:\n{response.text}")
            if response.tool_calls_made:
                tools = [tc["tool"] for tc in response.tool_calls_made]
                print(f"   [Tools executed: {', '.join(tools)}]")
            if response.escalated_to_human:
                print("   ⚠️ [Conversation escalated to human support ticket]")


if __name__ == "__main__":
    asyncio.run(interactive_chat())
