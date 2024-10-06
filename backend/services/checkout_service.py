import json
from typing import List
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy import update
from schemas.schemas import CartItemForCheckout
from config.parser import load_config
from models.models import Product
from exceptions.product_exceptions import ProductException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from services.product_service import ProductService
import stripe


class CheckoutService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.product_service = ProductService(session)

    async def update_stock_quantity(self, cart_items: List[CartItemForCheckout]):
        try:
            async with self.db.begin():
                update_statements = list()
                for item in cart_items:
                    stmt = select(Product).where(Product.id == item.id)
                    result = await self.db.execute(stmt)
                    product: Product = result.scalars().first()

                    if product is None:
                        raise ProductException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No product found with id {item.id}"
                        )

                    new_quantity = product.stock_quantity - item.quantity
                    update_stmt = update(Product).where(Product.id == item.id).values(stock_quantity=new_quantity)
                    update_statements.append(update_stmt)

                for update_stmt in update_statements:
                    await self.db.execute(update_stmt)

                await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def create_checkout_session(self, cart_items: List[CartItemForCheckout]):
        stripe.api_key = load_config().auth_config.stripe_secret_key

        metadata_dict = {
            "metadata_item_names": {},
            "product_category": "",
            "seller_id": ""
        }

        item_names = dict()
        seller_ids = list()

        for item in cart_items:
            product = await self.product_service.get_product_by_id(item.id)
            seller_ids.append(str(product.get("seller_id")))
            if item.name not in item_names:
                item_names[item.name] = item.quantity

        metadata_dict["metadata_item_names"] = json.dumps(item_names)
        metadata_dict["product_category"] = item.category
        metadata_dict["seller_id"] = ", ".join(seller_ids)

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{item.name}",
                        },
                        'unit_amount': item.price * 100,
                    },
                    'quantity': item.quantity,
                } for item in cart_items
            ],
            payment_intent_data={
                'metadata': metadata_dict,
            },
            mode='payment',
            success_url=load_config().server_config.frontend_domain + '?success=true',
            cancel_url=load_config().server_config.frontend_domain + '?canceled=true',
        )

        return {"session_id": checkout_session["id"]}
