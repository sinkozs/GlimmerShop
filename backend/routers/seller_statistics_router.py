from typing import List
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session
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
async def get_monthly_transactions(month_request: MonthRequestForSellerStatistics, session: AsyncSession = Depends(get_session)):
    service = SellerStatisticsService(session)
    controller = SellerStatisticsController(service)
    try:
        return await controller.get_monthly_transactions(month_request)
    except HTTPException as e:
        raise e
