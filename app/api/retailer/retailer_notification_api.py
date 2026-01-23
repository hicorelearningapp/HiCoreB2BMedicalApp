from fastapi import APIRouter, HTTPException
from typing import Optional
from ...config import settings
from ...crud.retailer.retailer_notification_manager import RetailerNotificationManager
from ...schemas.retailer.retailer_notification_schema import RetailerNotificationCreate


class RetailerNotificationAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = RetailerNotificationManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/retailers/notifications")(self.create_notification)
        self.router.get("/retailers/{retailer_id}/notifications")(self.get_notifications)
        self.router.put("/retailers/notifications/{notification_id}/read")(self.mark_as_read)
        self.router.delete("/retailers/notifications/{notification_id}")(self.delete_notification)
        self.router.delete("/retailers/{retailer_id}/notifications")(self.delete_all_notifications)

    # ------------------------------------------------------------
    # 🟢 Create Notification
    # ------------------------------------------------------------
    async def create_notification(self, notification: RetailerNotificationCreate):
        try:
            return await self.crud.create_notification(notification)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    # 🟡 Get Notifications by Retailer
    # ------------------------------------------------------------
    async def get_notifications(self, retailer_id: int):
        try:
            return await self.crud.get_notifications(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    # 🟠 Mark Notification as Read
    # ------------------------------------------------------------
    async def mark_as_read(self, notification_id: int):
        try:
            return await self.crud.mark_as_read(notification_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    # 🔴 Delete Single Notification
    # ------------------------------------------------------------
    async def delete_notification(self, notification_id: int):
        try:
            return await self.crud.delete_notification(notification_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------
    # 🗑️ Delete All Notifications for a Retailer
    # ------------------------------------------------------------
    async def delete_all_notifications(self, retailer_id: int):
        try:
            return await self.crud.delete_all_notifications(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
