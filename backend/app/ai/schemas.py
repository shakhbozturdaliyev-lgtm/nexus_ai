"""Pydantic schemas for AI tools and function calling."""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchProductsArgs(BaseModel):
    """Arguments for search_products tool."""
    query: str = Field(description="Search keyword for product name, brand, or model (e.g., 'Samsung A16', 'iPhone 16')")
    category_id: Optional[int] = Field(default=None, description="Optional category filter ID")
    min_price: Optional[float] = Field(default=None, description="Minimum price in UZS")
    max_price: Optional[float] = Field(default=None, description="Maximum price in UZS")


class GetProductDetailsArgs(BaseModel):
    """Arguments for get_product_details tool."""
    product_id: int = Field(description="Database product ID")


class CheckInventoryArgs(BaseModel):
    """Arguments for check_inventory tool."""
    product_id: int = Field(description="Database product ID")
    variant_id: Optional[int] = Field(default=None, description="Optional specific variant ID")


class GetBusinessHoursArgs(BaseModel):
    """Arguments for get_business_hours tool."""
    pass


class GetDeliveryPolicyArgs(BaseModel):
    """Arguments for get_delivery_policy tool."""
    region: Optional[str] = Field(default=None, description="Target city or region (e.g., 'Tashkent', 'Samarkand')")


class GetReturnPolicyArgs(BaseModel):
    """Arguments for get_return_policy tool."""
    pass


class GetFAQAnswerArgs(BaseModel):
    """Arguments for get_faq_answer tool."""
    question: str = Field(description="Customer question topic (e.g., 'payment', 'credit', 'warranty')")


class GetOrderStatusArgs(BaseModel):
    """Arguments for get_order_status tool."""
    order_number: str = Field(description="Unique order number (e.g., 'ORD-1001')")


class CreateSupportTicketArgs(BaseModel):
    """Arguments for create_support_ticket tool."""
    category: str = Field(description="Issue category: 'product', 'delivery', 'return', 'complaint', or 'general'")
    message: str = Field(description="Customer summary of the issue")


class RequestHumanHandoffArgs(BaseModel):
    """Arguments for request_human_handoff tool."""
    reason: str = Field(description="Reason for human escalation")


class AIResponse(BaseModel):
    """Unified response object returned by AI orchestrator."""
    text: str
    tool_calls_made: List[Dict[str, Any]] = Field(default_factory=list)
    escalated_to_human: bool = False
    language_used: str = "uz"
    tokens_used: int = 0
