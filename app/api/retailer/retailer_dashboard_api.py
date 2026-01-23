from fastapi import APIRouter, HTTPException
from ...crud.retailer.retailer_dashboard_manager import RetailerDashboardManager
from ...config import settings

class RetailerDashboardAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = RetailerDashboardManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.get("/retailer/{retailer_id}/dashboard")(self.get_dashboard)

    async def get_dashboard(self, retailer_id: int):
        try:
            return await self.manager.get_dashboard(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
