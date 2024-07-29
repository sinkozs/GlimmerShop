from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Request
import redis.asyncio as aioredis
from dependencies import get_session
from sqlalchemy.future import select
from schemas.schemas import CartItemForCheckout
from config.parser import load_config
from models.models import Product
from exceptions.product_exceptions import ProductException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import stripe


router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    responses={500: {"Checkout": "Error when creating checkout session"}}
)


async def update_stock_quantity(cart_items: List[CartItemForCheckout], db: AsyncSession = Depends(get_session)):
    async with db.begin():
        for item in cart_items:
            stmt = select(Product).where(Product.id == item.product_id)
            result = await db.execute(stmt)
            product: Product = result.scalars().first()

            if product is None:
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No product found with id {item.product_id}"
                )
            product.stock_quantity -= item.quantity
            db.add(product)
            await db.commit()
    return {200: "Successfully updated stock quantity!"}


@router.post("/create-checkout-session")
async def create_checkout_session(cart_items: List[CartItemForCheckout], session: AsyncSession = Depends(get_session)):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{item.product_name}",
                        },
                        'unit_amount': item.price,
                    },
                    'quantity': item.quantity,
                } for item in cart_items
            ],
            mode='payment',
            success_url=load_config().server_config.domain + '?success=true',
            cancel_url=load_config().server_config.domain + '?canceled=true',
        )
        await update_stock_quantity(cart_items, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
