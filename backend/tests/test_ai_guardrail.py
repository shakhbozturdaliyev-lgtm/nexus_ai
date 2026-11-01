"""Unit tests for hallucination detection guardrail."""

from backend.app.ai.guardrail import HallucinationGuardrail


def test_guardrail_allows_verified_price():
    """Verify that accurate prices matching tool results pass through unchanged."""
    tool_results = [
        {
            "products": [
                {
                    "name": "Samsung Galaxy A16",
                    "variants": [
                        {"price_uzs": 2450000.0, "stock_quantity": 15},
                        {"price_uzs": 2850000.0, "stock_quantity": 8},
                    ],
                }
            ]
        }
    ]
    response_text = "Samsung Galaxy A16 narxi 2,450,000 UZS va 2 850 000 UZS."
    verified = HallucinationGuardrail.verify_response(response_text, tool_results, lang="uz")
    assert verified == response_text


def test_guardrail_intercepts_hallucinated_price():
    """Verify that fabricated prices not present in tool results are intercepted."""
    tool_results = [
        {
            "products": [
                {
                    "name": "Samsung Galaxy A16",
                    "variants": [
                        {"price_uzs": 2450000.0, "stock_quantity": 15},
                    ],
                }
            ]
        }
    ]
    # LLM hallucinates 1,200,000 UZS which does not exist in catalog
    hallucinated_text = "Samsung Galaxy A16 narxi 1,200,000 so'm."
    verified = HallucinationGuardrail.verify_response(hallucinated_text, tool_results, lang="uz")

    assert verified != hallucinated_text
    assert "tasdiqlanmadi" in verified
    assert "operator" in verified
