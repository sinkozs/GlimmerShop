from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session, get_first_and_last_day_of_month
from sqlalchemy.future import select
from sqlalchemy import update
from schemas.schemas import MonthRequestForSellerStatistics
from config.parser import load_config
from models.models import Product
from exceptions.product_exceptions import ProductException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import stripe
from datetime import datetime, timedelta


class SellerStatisticsService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.key = load_config().auth_config.stripe_secret_key
        self.stripe_api_key = self.key

    def convert_metadata_to_dict(self, metadata):
        converted_dict = dict()

        for key, value in metadata.items():
            converted_dict[key] = value.split(", ")

        return converted_dict

    async def get_monthly_transactions(self, data: MonthRequestForSellerStatistics) -> Dict[str, any]:
        stripe.api_key = self.stripe_api_key
        first_day, last_day = get_first_and_last_day_of_month(data.month)

        charges = stripe.Charge.list(
            created={
                "gte": int(first_day.timestamp()),
                "lte": int(last_day.timestamp()),
            },
            status="succeeded",
            limit=100
        )

        total_revenue = 0
        total_transactions = len(charges['data'])
        items = dict()

        for charge in charges['data']:
            total_revenue += charge['amount']

            metadata = self.convert_metadata_to_dict(charge.get("metadata", {}))
            item_names = metadata.get("metadata_item_names", [])

            for item_name in item_names:
                items[item_name] = items.get(item_name, 0) + 1

        return {
            "total_transactions": total_transactions,
            "total_revenue": total_revenue / 100,
            "items": items
        }

