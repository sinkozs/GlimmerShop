from typing import List
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session
from sqlalchemy.future import select
from sqlalchemy import update
from schemas.schemas import CartItemForCheckout
from config.parser import load_config
from models.models import Product
from exceptions.product_exceptions import ProductException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import stripe


class CheckoutService:

    def __init__(self, session: AsyncSession):
        self.db = session

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

                # execute all update statements in one batch to improve performance
                for update_stmt in update_statements:
                    await self.db.execute(update_stmt)

                await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def create_checkout_session(self, cart_items: List[CartItemForCheckout]):
        try:
            print(cart_items)
            stripe.api_key = load_config().auth_config.stripe_secret_key

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
                mode='payment',
                success_url=load_config().server_config.frontend_domain + '?success=true',
                cancel_url=load_config().server_config.frontend_domain + '?canceled=true',
            )
            return {"session_id": checkout_session["id"]}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))