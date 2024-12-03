from uuid import UUID

from services.seller_statistics_service import SellerStatisticsService
from fastapi import HTTPException
from schemas.schemas import SelectedMonthForSellerStatistics


class SellerStatisticsController:

    def __init__(self, service: SellerStatisticsService):
        self._service = service

    async def get_monthly_transactions(
        self, seller_id: UUID, selected_date: SelectedMonthForSellerStatistics
    ):
        try:
            return await self._service.get_monthly_transactions(
                seller_id, selected_date
            )
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
