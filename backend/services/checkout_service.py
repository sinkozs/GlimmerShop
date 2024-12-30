import json
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update

from config.logger_config import get_logger
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
        self.logger = get_logger(__name__)

    async def update_stock_quantity(self, cart_items: List[CartItemForCheckout]):
        try:
            update_statements = list()
            for item in cart_items:
                stmt = select(Product).where(Product.id == item.id)
                result = await self.db.execute(stmt)
                product: Product = result.scalars().first()

                if product is None:
                    raise ProductException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No product found with id {item.id}",
                    )

                new_quantity = product.stock_quantity - item.quantity
                update_stmt = (
                    update(Product)
                    .where(Product.id == item.id)
                    .values(stock_quantity=new_quantity)
                )
                update_statements.append(update_stmt)

            for update_stmt in update_statements:
                await self.db.execute(update_stmt)

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in update_stock_quantity: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def create_checkout_session(self, cart_items: List[CartItemForCheckout]):
        stripe.api_key = load_config().auth_config.stripe_secret_key

        metadata_dict = {
            "product_quantities": {},
            "product_categories": {},
            "seller_id": "",
        }

        product_quantities = dict()
        product_categories = dict()
        seller_ids = list()

        for item in cart_items:
            product = await self.product_service.get_product_by_id(item.id)
            seller_ids.append(str(product.get("seller_id")))
            category_id = item.category
            print(category_id)
            if item.name not in product_quantities:
                product_quantities[item.name] = item.quantity
            if item.category not in product_categories.keys():
                product_categories[item.category] = item.quantity
            elif item.category in product_categories.keys():
                product_categories[item.category] += item.quantity

        metadata_dict["product_quantities"] = json.dumps(product_quantities)
        metadata_dict["product_categories"] = json.dumps(product_categories)
        metadata_dict["seller_id"] = ", ".join(seller_ids)

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{item.name}",
                        },
                        "unit_amount": item.price * 100,
                    },
                    "quantity": item.quantity,
                }
                for item in cart_items
            ],
            payment_intent_data={
                "metadata": metadata_dict,
            },
            mode="payment",
            success_url=load_config().server_config.frontend_domain + "?success=true",
            cancel_url=load_config().server_config.frontend_domain + "?canceled=true",
        )

        return {"session_id": checkout_session["id"]}
