"""Add flagship products (S23 Ultra, S24 Ultra) to live database if not present."""

import asyncio
import sys
from decimal import Decimal
from pathlib import Path

# Add root dir to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.category import Category
from backend.app.models.product import Product, ProductVariant


async def main():
    async with AsyncSessionLocal() as session:
        # Check smartphones category
        cat_res = await session.execute(
            select(Category).where(Category.business_id == 1, Category.slug == "smartphones")
        )
        cat = cat_res.scalar_one_or_none()
        if not cat:
            print("Category smartphones not found!")
            return

        # 1. Samsung Galaxy S23 Ultra
        s23_res = await session.execute(
            select(Product).where(Product.business_id == 1, Product.name == "Samsung Galaxy S23 Ultra")
        )
        s23 = s23_res.scalar_one_or_none()
        if not s23:
            s23 = Product(
                business_id=1,
                category_id=cat.id,
                name="Samsung Galaxy S23 Ultra",
                brand="Samsung",
                description="6.8-inch Dynamic AMOLED 2X 120Hz display, Snapdragon 8 Gen 2, 200MP Quad Camera with 100x Space Zoom, S-Pen included, 5000mAh battery.",
                currency="UZS",
                active_status=True,
            )
            session.add(s23)
            await session.flush()

            v1 = ProductVariant(
                product_id=s23.id,
                sku="SAM-S23U-256-BLK",
                storage_capacity="256 GB",
                color="Phantom Black",
                price=Decimal("13800000.00"),
                stock_quantity=8,
                availability_status="in_stock",
            )
            v2 = ProductVariant(
                product_id=s23.id,
                sku="SAM-S23U-512-GRN",
                storage_capacity="512 GB",
                color="Green",
                price=Decimal("15200000.00"),
                stock_quantity=5,
                availability_status="in_stock",
            )
            v3 = ProductVariant(
                product_id=s23.id,
                sku="SAM-S23U-1TB-BLK",
                storage_capacity="1 TB",
                color="Phantom Black",
                price=Decimal("17500000.00"),
                stock_quantity=3,
                availability_status="in_stock",
            )
            session.add_all([v1, v2, v3])
            print("Added Samsung Galaxy S23 Ultra with 256GB, 512GB, 1TB variants.")

        # 2. Samsung Galaxy S24 Ultra
        s24_res = await session.execute(
            select(Product).where(Product.business_id == 1, Product.name == "Samsung Galaxy S24 Ultra")
        )
        s24 = s24_res.scalar_one_or_none()
        if not s24:
            s24 = Product(
                business_id=1,
                category_id=cat.id,
                name="Samsung Galaxy S24 Ultra",
                brand="Samsung",
                description="Galaxy AI, Titanium Frame, 6.8-inch Flat Dynamic AMOLED 2X 120Hz, Snapdragon 8 Gen 3 for Galaxy, 200MP Quad Camera, S-Pen.",
                currency="UZS",
                active_status=True,
            )
            session.add(s24)
            await session.flush()

            v1 = ProductVariant(
                product_id=s24.id,
                sku="SAM-S24U-256-GRY",
                storage_capacity="256 GB",
                color="Titanium Gray",
                price=Decimal("15900000.00"),
                stock_quantity=10,
                availability_status="in_stock",
            )
            v2 = ProductVariant(
                product_id=s24.id,
                sku="SAM-S24U-512-BLK",
                storage_capacity="512 GB",
                color="Titanium Black",
                price=Decimal("17800000.00"),
                stock_quantity=6,
                availability_status="in_stock",
            )
            v3 = ProductVariant(
                product_id=s24.id,
                sku="SAM-S24U-1TB-VIO",
                storage_capacity="1 TB",
                color="Titanium Violet",
                price=Decimal("20400000.00"),
                stock_quantity=2,
                availability_status="in_stock",
            )
            session.add_all([v1, v2, v3])
            print("Added Samsung Galaxy S24 Ultra with 256GB, 512GB, 1TB variants.")

        await session.commit()
        print("Flagships successfully committed.")


if __name__ == "__main__":
    asyncio.run(main())
