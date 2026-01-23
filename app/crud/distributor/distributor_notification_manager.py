from ...utils.timezone import ist_now
from typing import Optional, List
from ...db.base.database_manager import DatabaseManager
from ...models.distributor.distributor_notification_model import DistributorNotification
from ...schemas.distributor.distributor_notification_schema import (
    DistributorNotificationCreate,
    DistributorNotificationUpdate
)
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DistributorNotificationManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    # ------------------------------------------------------------
    # 🟢 Create Notification
    # ------------------------------------------------------------
    async def create_notification(self, notification: DistributorNotificationCreate) -> dict:
        try:
            await self.db_manager.connect()
            data = notification.dict()
            data["Date"] = ist_now()
            await self.db_manager.create(DistributorNotification, data)

            logger.info(f"✅ Distributor Notification created: {data['Title']}")
            return {"success": True, "message": "Notification created successfully"}
        except Exception as e:
            logger.error(f"❌ Error creating notification: {e}")
            return {"success": False, "message": f"Error creating notification: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟡 Get All Notifications (by distributor)
    # ------------------------------------------------------------
    async def get_notifications(self, distributor_id: int) -> dict:
        try:
            await self.db_manager.connect()
            notifications = await self.db_manager.read(
                DistributorNotification, {"DistributorId": distributor_id}
            )
            total = len(notifications)
            unread = len([n for n in notifications if not n.IsRead])
            order_related = len([n for n in notifications if "order" in n.Type.lower()])
            stock_related = len([n for n in notifications if "stock" in n.Type.lower()])

            return {
                "Total": total,
                "Unread": unread,
                "Orders": order_related,
                "StockAlerts": stock_related,
                "Notifications": notifications,
            }
        except Exception as e:
            logger.error(f"❌ Error fetching distributor notifications: {e}")
            return {"success": False, "message": f"Error fetching notifications: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟠 Mark Notification as Read
    # ------------------------------------------------------------
    async def mark_as_read(self, notification_id: int) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.update(
                DistributorNotification, {"NotificationId": notification_id}, {"IsRead": True}
            )
            if rowcount:
                logger.info(f"✅ Distributor Notification {notification_id} marked as read")
                return {"success": True, "message": "Notification marked as read"}
            return {"success": False, "message": "Notification not found"}
        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {e}")
            return {"success": False, "message": f"Error marking notification as read: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🔴 Delete Notification
    # ------------------------------------------------------------
    async def delete_notification(self, notification_id: int) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.delete(
                DistributorNotification, {"NotificationId": notification_id}
            )
            if rowcount:
                logger.info(f"🗑️ Distributor Notification {notification_id} deleted")
                return {"success": True, "message": "Notification deleted successfully"}
            return {"success": False, "message": "Notification not found"}
        except Exception as e:
            logger.error(f"❌ Error deleting distributor notification {notification_id}: {e}")
            return {"success": False, "message": f"Error deleting notification: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🗑️ Delete All Notifications for Distributor
    # ------------------------------------------------------------
    async def delete_all_notifications(self, distributor_id: int) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.delete(
                DistributorNotification, {"DistributorId": distributor_id}
            )
            if rowcount:
                logger.info(f"🧹 Deleted all notifications for Distributor {distributor_id}")
                return {"success": True, "message": f"Deleted {rowcount} notifications"}
            return {"success": False, "message": "No notifications found to delete"}
        except Exception as e:
            logger.error(f"❌ Error deleting distributor notifications: {e}")
            return {"success": False, "message": f"Error deleting notifications: {e}"}
        finally:
            await self.db_manager.disconnect()
