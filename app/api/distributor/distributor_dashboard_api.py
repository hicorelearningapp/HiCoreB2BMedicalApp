from fastapi import APIRouter, HTTPException
from ...crud.distributor.distributor_dashboard_manager import DistributorDashboardManager
from ...config import settings

class DistributorDashboardAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = DistributorDashboardManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.get("/distributor/{distributor_id}/dashboard/")(self.get_dashboard)

    async def get_dashboard(self, distributor_id: int):
        try:
            return await self.manager.get_dashboard(distributor_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
