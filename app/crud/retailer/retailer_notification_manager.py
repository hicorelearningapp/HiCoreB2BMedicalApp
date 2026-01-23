from ...utils.timezone import ist_now
from typing import Optional, List
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_notification_model import RetailerNotification
from ...schemas.retailer.retailer_notification_schema import RetailerNotificationCreate, RetailerNotificationUpdate
from ...utils.logger import get_logger

logger = get_logger(__name__)


class RetailerNotificationManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    # ------------------------------------------------------------
    # 🟢 Create Notification
    # ------------------------------------------------------------
    async def create_notification(self, notification: RetailerNotificationCreate) -> dict:
        try:
            await self.db_manager.connect()
            data = notification.dict()
            data["Date"] = ist_now()
            await self.db_manager.create(RetailerNotification, data)

            logger.info(f"✅ Notification created: {data['Title']}")
            return {"success": True, "message": "Notification created successfully"}
        except Exception as e:
            logger.error(f"❌ Error creating notification: {e}")
            return {"success": False, "message": f"Error creating notification: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟡 Get All Notifications (by retailer)
    # ------------------------------------------------------------
    async def get_notifications(self, retailer_id: int) -> dict:
        try:
            await self.db_manager.connect()
            notifications = await self.db_manager.read(
                RetailerNotification, {"RetailerId": retailer_id}
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
            logger.error(f"❌ Error fetching notifications: {e}")
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
                RetailerNotification, {"NotificationId": notification_id}, {"IsRead": True}
            )
            if rowcount:
                logger.info(f"✅ Notification {notification_id} marked as read")
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
                RetailerNotification, {"NotificationId": notification_id}
            )
            if rowcount:
                logger.info(f"🗑️ Notification {notification_id} deleted successfully")
                return {"success": True, "message": "Notification deleted successfully"}
            return {"success": False, "message": "Notification not found"}
        except Exception as e:
            logger.error(f"❌ Error deleting notification {notification_id}: {e}")
            return {"success": False, "message": f"Error deleting notification: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🗑️ Delete All Notifications for a Retailer
    # ------------------------------------------------------------
    async def delete_all_notifications(self, retailer_id: int) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.delete(
                RetailerNotification, {"RetailerId": retailer_id}
            )
            if rowcount:
                logger.info(f"🧹 Deleted all notifications for Retailer {retailer_id}")
                return {"success": True, "message": f"Deleted {rowcount} notifications"}
            return {"success": False, "message": "No notifications found to delete"}
        except Exception as e:
            logger.error(f"❌ Error deleting all notifications for retailer {retailer_id}: {e}")
            return {"success": False, "message": f"Error deleting notifications: {e}"}
        finally:
            await self.db_manager.disconnect()


