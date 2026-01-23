from fastapi import APIRouter, HTTPException
from typing import Optional
from ...crud.distributor.distributor_report_manager import DistributorReportManager
from ...config import settings

class DistributorReportAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = DistributorReportManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.get("/distributor/sales-dashboard/{distributor_id}")(self.sales_dashboard)

    # -----------------------------
    # Distributor Sales Dashboard
    # -----------------------------
    async def sales_dashboard(self, distributor_id: int):
        """
        Returns sales analytics for a distributor, including:
        - TotalRevenue
        - TotalOrders
        - AvgOrderValue
        - SalesTrend per month
        - OrderVolume per month
        - TopSellingProduct
        """
        try:
            return await self.manager.get_sales_dashboard(distributor_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
