import json
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update

from config.logger_config import get_logger
from schemas.schemas import CartItemForCheckout, OrderData
from config.parser import load_config
from models.models import Product
from exceptions.product_exceptions import ProductException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from services.order_service import OrderService
from services.product_service import ProductService
import stripe


class CheckoutService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.product_service = ProductService(session)
        self.logger = get_logger(__name__)

    async def update_stock_quantity(self, orders: List[OrderData]) -> None:
        try:
            print("UPDATE STOCK")
            for order in orders:
                stmt = select(Product).where(Product.id == order.product_id)
                result = await self.db.execute(stmt)
                product = result.scalars().first()

                if product is None:
                    raise ProductException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No product found with id {order.product_id}"
                    )

                if product.stock_quantity < order.quantity:
                    raise ProductException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for product {product.id}. "
                               f"Requested: {order.quantity}, Available: {product.stock_quantity}"
                    )

            # Then update all products
            for order in orders:
                update_stmt = (
                    update(Product)
                    .where(Product.id == order.product_id)
                    .values(
                        stock_quantity=Product.stock_quantity - order.quantity
                    )
                )
                await self.db.execute(update_stmt)

            # Single commit after all updates
            await self.db.commit()

        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"Database error in update_stock_quantity: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!"
            )

    async def create_checkout_session(self, cart_items: List[CartItemForCheckout]):
        stripe.api_key = load_config().auth_config.stripe_secret_key
        metadata_dict = {
            "product_quantities": {},
            "product_categories": {},
            "seller_id": "",
        }

        order_data_list = []
        validated_line_items = []
        product_quantities = dict()
        product_categories = dict()
        seller_ids = list()

        # Validation
        for item in cart_items:
            product = await self.product_service.get_product_by_id(item.id)

            if not product:
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.id} not found"
                )

            actual_price = product.get("price")
            if actual_price != item.price:
                raise ProductException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Price mismatch for product {item.name}"
                )

            if product.get("stock_quantity") < item.quantity:
                raise ProductException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {item.name}"
                )

            stripe_amount = int(actual_price * 100)

            validated_line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product.get("name"),
                    },
                    "unit_amount": stripe_amount,
                },
                "quantity": item.quantity,
            })

            seller_ids.append(str(product.get("seller_id")))
            order_data = OrderData(
                product_id=product["id"],
                price=product["price"],
                quantity=item.quantity
            )
            order_data_list.append(order_data)

            if item.name not in product_quantities:
                product_quantities[item.name] = item.quantity

            if item.category not in product_categories:
                product_categories[item.category] = item.quantity
            else:
                product_categories[item.category] += item.quantity

        metadata_dict["product_quantities"] = json.dumps(product_quantities)
        metadata_dict["product_categories"] = json.dumps(product_categories)
        metadata_dict["seller_id"] = ", ".join(seller_ids)

        checkout_session = stripe.checkout.Session.create(
            line_items=validated_line_items,
            payment_intent_data={
                "metadata": metadata_dict,
            },
            mode="payment",
            success_url=load_config().server_config.frontend_domain + "?success=true",
            cancel_url=load_config().server_config.frontend_domain + "?canceled=true",
        )
        print(f"SERVICE SESSION ID: {checkout_session['id']}")
        return {"session_id": checkout_session['id'], "order_data": order_data_list}
