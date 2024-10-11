from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session, get_current_user
from sqlalchemy.future import select
from schemas.schemas import MonthRequestForSellerStatistics
from config.parser import load_config
from models.models import Product
from exceptions.product_exceptions import ProductException
from services.seller_statistics_service import SellerStatisticsService
from controllers.seller_statistics_controller import SellerStatisticsController
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import stripe

router = APIRouter(
    prefix="/seller-statistics",
    tags=["seller-statistics"],
    responses={500: {"Seller Statistics": "Error when fetching Seller statistics"}}
)


@router.post("/get-monthly-transactions")
async def get_monthly_transactions(month_request: MonthRequestForSellerStatistics,
                                   current_user: dict = Depends(get_current_user),
                                   session: AsyncSession = Depends(get_session)):
    service = SellerStatisticsService(session)
    controller = SellerStatisticsController(service)
    try:
        seller_id: UUID = current_user.get("id")
        if not seller_id:
            raise HTTPException(status_code=400, detail="Missing seller ID")
        data = await controller.get_monthly_transactions(seller_id, month_request)
        print(data)
        return data
    except HTTPException as e:
        raise e
