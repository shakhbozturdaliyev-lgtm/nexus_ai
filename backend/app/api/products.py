"""Product catalog and inventory management API router."""

import csv
import io
from decimal import Decimal
from typing import Annotated, Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.models.product import Product, ProductVariant
from backend.app.models.user import User

router = APIRouter(prefix="/api/products", tags=["Products"])


class VariantInput(BaseModel):
    sku: str
    storage_capacity: Optional[str] = None
    color: Optional[str] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)


class ProductCreateRequest(BaseModel):
    name: str
    brand: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    currency: str = "UZS"
    variants: List[VariantInput]


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    active_status: Optional[bool] = None


@router.get("")
async def list_products(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Optional[str] = None,
):
    """List business catalog products and variants."""
    stmt = (
        select(Product)
        .where(Product.business_id == current_user.business_id)
        .order_by(Product.name.asc())
    )
    if search:
        stmt = stmt.where(Product.name.ilike(f"%{search}%") | Product.brand.ilike(f"%{search}%"))

    res = await db.execute(stmt)
    products = res.scalars().all()

    output = []
    for p in products:
        v_res = await db.execute(
            select(ProductVariant).where(ProductVariant.product_id == p.id)
        )
        variants = v_res.scalars().all()
        output.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "description": p.description,
            "currency": p.currency,
            "active_status": p.active_status,
            "created_at": p.created_at.isoformat(),
            "variants": [
                {
                    "id": v.id,
                    "sku": v.sku,
                    "storage_capacity": v.storage_capacity,
                    "color": v.color,
                    "price": float(v.price),
                    "stock_quantity": v.stock_quantity,
                    "availability_status": v.availability_status,
                }
                for v in variants
            ],
        })

    return {"count": len(output), "items": output}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(
    req: ProductCreateRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create new product and initial variants."""
    product = Product(
        business_id=current_user.business_id,
        category_id=req.category_id,
        name=req.name,
        brand=req.brand,
        description=req.description,
        currency=req.currency,
        active_status=True,
    )
    db.add(product)
    await db.flush()

    for v_in in req.variants:
        variant = ProductVariant(
            product_id=product.id,
            sku=v_in.sku,
            storage_capacity=v_in.storage_capacity,
            color=v_in.color,
            price=Decimal(str(v_in.price)),
            stock_quantity=v_in.stock_quantity,
            availability_status="in_stock" if v_in.stock_quantity > 0 else "out_of_stock",
        )
        db.add(variant)

    await db.commit()
    return {"status": "created", "product_id": product.id}


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    req: ProductUpdateRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update product details or active status."""
    res = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.business_id == current_user.business_id,
        )
    )
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if req.name is not None:
        product.name = req.name
    if req.brand is not None:
        product.brand = req.brand
    if req.description is not None:
        product.description = req.description
    if req.active_status is not None:
        product.active_status = req.active_status

    await db.commit()
    return {"status": "updated", "product_id": product.id}


@router.delete("/{product_id}")
async def deactivate_product(
    product_id: int,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Deactivate a product from active catalog."""
    res = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.business_id == current_user.business_id,
        )
    )
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    product.active_status = False
    await db.commit()
    return {"status": "deactivated", "product_id": product.id}


@router.get("/export-csv")
async def export_csv(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Export product catalog and variants as CSV file."""
    stmt = (
        select(Product, ProductVariant)
        .join(ProductVariant, Product.id == ProductVariant.product_id)
        .where(Product.business_id == current_user.business_id)
    )
    res = await db.execute(stmt)
    rows = res.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Product Name", "Brand", "Description", "SKU", "Storage", "Color", "Price UZS", "Stock Quantity", "Status"
    ])

    for prod, var in rows:
        writer.writerow([
            prod.name,
            prod.brand,
            prod.description or "",
            var.sku,
            var.storage_capacity or "",
            var.color or "",
            float(var.price),
            var.stock_quantity,
            var.availability_status,
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=nexus_catalog.csv"},
    )
