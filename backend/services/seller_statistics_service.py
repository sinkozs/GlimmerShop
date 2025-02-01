from typing import Dict
from uuid import UUID
from fastapi import HTTPException
from dependencies import get_first_and_last_day_of_month
from schemas.schemas import SelectedMonthForSellerStatistics
from services.category_service import CategoryService
from config.parser import load_config
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
import ast


class SellerStatisticsService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.key = load_config().auth_config.stripe_secret_key
        self.stripe_api_key = self.key
        self._category_service = CategoryService(session)

    def convert_metadata_to_dict(self, metadata):
        converted_dict = dict()

        for key, value in metadata.items():
            converted_dict[key] = value.split(", ")

        return converted_dict

    def get_dict_from_json_object(self, item: str) -> dict:
        fixed_item = item.translate(str.maketrans("", "", "{}"))
        item_dict = ast.literal_eval("{" + fixed_item + "}")
        return item_dict

    async def get_category_name(self, category_id: str):
        try:
            int_category_id = int(category_id)
            return await self._category_service.get_category_by_id(int_category_id)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid category ID format: {category_id}"
            )

    def is_seller_had_transactions(self, seller_id: UUID, charges) -> bool:
        if charges["data"]:
            for charge in charges["data"]:
                metadata = self.convert_metadata_to_dict(charge.get("metadata", {}))
                seller_id_metadata = metadata.get("seller_id", [])
                if str(seller_id) in seller_id_metadata:
                    return True
            return False

    async def get_monthly_transactions(
        self, seller_id: UUID, selected_date: SelectedMonthForSellerStatistics
    ) -> Dict[str, any]:
        stripe.api_key = self.stripe_api_key
        first_day, last_day = get_first_and_last_day_of_month(selected_date)

        charges = stripe.Charge.list(
            created={
                "gte": int(first_day.timestamp()),
                "lte": int(last_day.timestamp()),
            },
            status="succeeded",
            limit=100,
        )

        total_revenue = 0
        total_transactions = 0
        product_quantities = dict()
        product_categories = dict()
        item_unit_prices = dict()
        is_seller_had_transactions = self.is_seller_had_transactions(seller_id, charges)

        if charges["data"] and is_seller_had_transactions:
            for charge in charges["data"]:
                metadata = self.convert_metadata_to_dict(charge.get("metadata", {}))
                seller_id_metadata = metadata.get("seller_id", [])[0]

                if str(seller_id_metadata) == seller_id:
                    total_revenue += charge["amount"]
                    total_transactions += 1
                    product_quantities_list = metadata.get("product_quantities", [])
                    product_categories_list = metadata.get("product_categories", [])

                    for item in product_quantities_list:
                        for item_name, quantity in self.get_dict_from_json_object(
                            item
                        ).items():
                            if item_name in product_quantities:
                                product_quantities[item_name] += quantity
                            else:
                                product_quantities[item_name] = quantity
                                item_unit_prices[item_name] = (
                                    charge["amount"] / quantity / 100
                                )
                    for item in product_categories_list:
                        for category_id, quantity in self.get_dict_from_json_object(
                            item
                        ).items():

                            category_data = await self.get_category_name(category_id)
                            category_name = category_data["category_name"]
                            if category_name not in product_categories.keys():
                                product_categories[category_name] = quantity
                            else:
                                product_categories[category_name] += quantity

            return {
                "total_transactions": total_transactions,
                "total_revenue": total_revenue / 100,
                "product_quantities": product_quantities,
                "product_categories": product_categories,
                "item_unit_prices": item_unit_prices,
            }

        else:
            raise HTTPException(
                status_code=204,
                detail=f"There were no transactions in {selected_date.month}",
            )
