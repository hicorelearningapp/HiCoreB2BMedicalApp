from fastapi import APIRouter, HTTPException
from typing import Optional
from ...crud.retailer.retailer_report_manager import RetailerReportManager
from ...config import settings

class RetailerReportAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = RetailerReportManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.get("/retailer/sales-dashboard/{retailer_id}")(self.sales_dashboard)

    # -----------------------------
    # Retailer Sales Dashboard
    # -----------------------------
    async def sales_dashboard(self, retailer_id: int):
        """
        Returns sales analytics for a retailer, including:
        - TotalRevenue
        - TotalOrders
        - AvgOrderValue
        - SalesTrend per month
        - OrderVolume per month
        - TopSellingProduct
        """
        try:
            return await self.manager.get_sales_dashboard(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
