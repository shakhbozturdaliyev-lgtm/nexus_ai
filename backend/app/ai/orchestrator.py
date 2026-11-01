"""AI Orchestration Facade: coordinates defenses, engines, guardrails, and tools."""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.ai.defense import check_prompt_injection, redact_secrets, sanitize_input
from backend.app.ai.gemini_engine import GeminiAIEngine
from backend.app.ai.guardrail import HallucinationGuardrail
from backend.app.ai.mock_engine import MockAIEngine
from backend.app.ai.schemas import AIResponse
from backend.app.bot.session import get_conversation_history, save_message
from backend.app.core.config import settings
from backend.app.core.logging import logger


class AIOrchestrator:
    """Master controller governing all customer support AI interactions."""

    def __init__(self):
        self.mock_engine = MockAIEngine()
        self.gemini_engine = None
        if settings.gemini_api_key and not settings.ai_mock_mode:
            try:
                self.gemini_engine = GeminiAIEngine()
            except Exception as e:
                logger.warning(f"Could not initialize Gemini engine: {e}. Defaulting to mock engine.")

    async def process_message(
        self,
        db: AsyncSession,
        business_id: int,
        customer_id: int,
        conversation_id: int,
        user_message: str,
        lang: str = "uz",
    ) -> AIResponse:
        """Execute full AI processing pipeline with multi-layer defense and fallback."""
        # 1. Sanitize input
        cleaned_input = sanitize_input(user_message)

        # 2. Defense: Check for prompt injection
        is_injection, reason = check_prompt_injection(cleaned_input)
        if is_injection:
            logger.warning(f"Deflected prompt injection for Customer ID {customer_id}: {reason}")
            deflection_msgs = {
                "uz": (
                    "Kechirasiz, men faqat Demo Electronics mahsulotlari, narxlari va "
                    "do'kon xizmatlari bo'yicha yordam bera olaman. Sizga qaysi mahsulot kerak?"
                ),
                "ru": (
                    "Извините, я виртуальный консультант Demo Electronics и отвечаю "
                    "только на вопросы о товарах, ценах и условиях доставки."
                ),
                "en": (
                    "I am the virtual support assistant for Demo Electronics and can only "
                    "assist with product inquiries, prices, orders, and store policies."
                ),
            }
            deflected_text = deflection_msgs.get(lang, deflection_msgs["uz"])
            # Save deflected turn
            await save_message(
                db,
                conversation_id=conversation_id,
                sender_type="ai",
                content=deflected_text,
            )
            await db.commit()
            return AIResponse(
                text=deflected_text,
                tool_calls_made=[],
                escalated_to_human=False,
                language_used=lang,
                tokens_used=10,
            )

        # 3. Retrieve conversation history for sliding context window
        history_records = await get_conversation_history(
            db, conversation_id=conversation_id, limit=settings.max_context_window_turns
        )
        formatted_history = [
            {"role": m.sender_type, "content": m.content} for m in history_records
        ]

        # 4. Engine execution with graceful fallback
        ai_response: Optional[AIResponse] = None
        if self.gemini_engine and not settings.ai_mock_mode:
            try:
                ai_response = await self.gemini_engine.generate_response(
                    db=db,
                    business_id=business_id,
                    customer_id=customer_id,
                    conversation_id=conversation_id,
                    user_message=cleaned_input,
                    lang=lang,
                    history=formatted_history,
                )
            except Exception as e:
                logger.error(f"Gemini execution error, falling back to mock engine: {e}")

        # Fallback to Mock AI Engine if Gemini is absent or failed
        if not ai_response:
            ai_response = await self.mock_engine.generate_response(
                db=db,
                business_id=business_id,
                customer_id=customer_id,
                conversation_id=conversation_id,
                user_message=cleaned_input,
                lang=lang,
                history=formatted_history,
            )

        # 5. Hallucination Guardrail: Verify prices against database tool results
        verified_text = HallucinationGuardrail.verify_response(
            response_text=ai_response.text,
            tool_results=[tc.get("result", {}) for tc in ai_response.tool_calls_made],
            lang=lang,
        )

        # 6. Secret Redaction: Prevent accidental credential exposure
        safe_text = redact_secrets(verified_text)
        ai_response.text = safe_text

        # 7. Persist AI response message in conversation
        await save_message(
            db,
            conversation_id=conversation_id,
            sender_type="ai",
            content=safe_text,
        )
        await db.commit()

        return ai_response


# Global orchestrator singleton
orchestrator = AIOrchestrator()
