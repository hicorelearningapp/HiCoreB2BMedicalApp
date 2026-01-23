from fastapi import APIRouter, HTTPException
from typing import Optional
from ...config import settings
from ...crud.distributor.distributor_notification_manager import DistributorNotificationManager
from ...schemas.distributor.distributor_notification_schema import DistributorNotificationCreate


class DistributorNotificationAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = DistributorNotificationManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/distributors/notifications")(self.create_notification)
        self.router.get("/distributors/{distributor_id}/notifications")(self.get_notifications)
        self.router.put("/distributors/notifications/{notification_id}/read")(self.mark_as_read)
        self.router.delete("/distributors/notifications/{notification_id}")(self.delete_notification)
        self.router.delete("/distributors/{distributor_id}/notifications")(self.delete_all_notifications)

    # ------------------------------------------------------------
    async def create_notification(self, notification: DistributorNotificationCreate):
        try:
            return await self.crud.create_notification(notification)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    async def get_notifications(self, distributor_id: int):
        try:
            return await self.crud.get_notifications(distributor_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    async def mark_as_read(self, notification_id: int):
        try:
            return await self.crud.mark_as_read(notification_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    async def delete_notification(self, notification_id: int):
        try:
            return await self.crud.delete_notification(notification_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    async def delete_all_notifications(self, distributor_id: int):
        try:
            return await self.crud.delete_all_notifications(distributor_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
