from uuid import UUID

from services.seller_statistics_service import SellerStatisticsService
from schemas.schemas import CartItemForCheckout
from typing import List
from fastapi import HTTPException, Depends
from schemas.schemas import MonthRequestForSellerStatistics


class SellerStatisticsController:

    def __init__(self, service: SellerStatisticsService):
        self._service = service

    async def get_monthly_transactions(self, seller_id: UUID, month_request: MonthRequestForSellerStatistics):
        try:
            return await self._service.get_monthly_transactions(seller_id, month_request)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
