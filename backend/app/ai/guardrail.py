"""Hallucination prevention guardrail and deterministic fact reconciler."""

import re
from typing import Any, Dict, List, Set
from backend.app.core.logging import logger


class HallucinationGuardrail:
    """Validates factual claims (prices, inventory, SKUs) against verified database tool results."""

    @classmethod
    def verify_response(
        cls,
        response_text: str,
        tool_results: List[Dict[str, Any]],
        lang: str = "uz",
    ) -> str:
        """Inspect outbound response text and reconcile numerical claims against verified tool results."""
        if not tool_results:
            return response_text

        # Collect verified prices and quantities from tool results
        verified_prices: Set[int] = set()
        has_products = False

        for tr in tool_results:
            products = tr.get("products", [])
            if products:
                has_products = True
            for p in products:
                for v in p.get("variants", []):
                    price = v.get("price_uzs")
                    if price is not None:
                        verified_prices.add(int(price))

            # Also check single product details
            for v in tr.get("variants", []):
                price = v.get("price_uzs")
                if price is not None:
                    verified_prices.add(int(price))
                    has_products = True

            # Also check orders and order status results
            if "total_amount_uzs" in tr and tr["total_amount_uzs"] is not None:
                verified_prices.add(int(tr["total_amount_uzs"]))
            if "unit_price_uzs" in tr and tr["unit_price_uzs"] is not None:
                verified_prices.add(int(tr["unit_price_uzs"]))

        # Mask out phone numbers and order numbers before checking for prices
        sanitized_text = re.sub(r"\+?998[\s-]?\d{2}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}", " ", response_text)
        sanitized_text = re.sub(r"\bORD-[A-Za-z0-9-]+\b", " ", sanitized_text)
        sanitized_text = re.sub(r"\b\d{9,12}\b", " ", sanitized_text)  # Mask phone numbers

        # Extract large numeric values that look like UZS prices (e.g. 2 450 000, 2450000, 12,800,000)
        raw_numbers = re.findall(
            r"\b\d{1,3}(?:[ ,.]\d{3})+(?:\s*(?:so'm|som|сум|uzs))?\b|\b\d{6,9}\s*(?:so'm|som|сум|uzs)\b",
            sanitized_text,
            re.IGNORECASE,
        )

        unverified_found = False
        for num_str in raw_numbers:
            # Strip formatting
            clean_digits = re.sub(r"[^\d]", "", num_str)
            if clean_digits:
                val = int(clean_digits)
                # If it's a price-like figure (e.g. > 500,000) and not in verified prices
                if val >= 500000 and verified_prices and val not in verified_prices:
                    logger.warning(
                        f"Hallucination Guardrail caught unverified price: {val} UZS in text: '{num_str}'. Verified were: {verified_prices}"
                    )
                    unverified_found = True
                    break

        if unverified_found:
            fallback_msgs = {
                "uz": (
                    "Kechirasiz, ushbu mahsulotning ayni paytdagi narxi tasdiqlanmadi. "
                    "Aniq ma'lumot olish uchun sizni operatorimiz bilan bog'lashimizni xohlaysizmi?"
                ),
                "ru": (
                    "К сожалению, точная цена на данный товар не подтверждена. "
                    "Хотите, я свяжу вас с оператором службы поддержки?"
                ),
                "en": (
                    "I could not verify the current price for this item. "
                    "Would you like me to connect you with a customer support representative?"
                ),
            }
            return fallback_msgs.get(lang, fallback_msgs["uz"])

        return response_text
