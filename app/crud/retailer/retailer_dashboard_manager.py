from typing import List, Dict
from datetime import datetime
from ...db.base.database_manager import DatabaseManager
from ...models.customer.order_model import Order
from ...models.retailer.retailer_inventory_model import RetailerInventory

class RetailerDashboardManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def get_dashboard(self, retailer_id: int) -> Dict:
        await self.db_manager.connect()

        try:
            # ----------------------
            # Today's sales
            # ----------------------
            today = datetime.today().date()
            orders = await self.db_manager.read(Order, {"RetailerId": retailer_id})
            orders_today = [o for o in orders if o.OrderDateTime.date() == today]
            today_sales = sum(o.Amount for o in orders_today)
            new_orders_count = len([o for o in orders_today if o.OrderStage == "New"])

            # ----------------------
            # New Orders List
            # ----------------------
            new_orders_list = [
                {"OrderID": o.OrderId, "CustomerName": o.CustomerName, "Price": o.Amount}
                for o in orders_today if o.OrderStage == "New"
            ]

            # ----------------------
            # Recent Orders List
            # ----------------------
            recent_orders = await self.db_manager.read(Order, {"RetailerId": retailer_id})
            recent_orders_list = [
                {"OrderID": o.OrderId, "CustomerName": o.CustomerName, "Price": o.Amount, "Status": o.OrderStatus}
                for o in recent_orders
            ]

            # ----------------------
            # Low Stock Medicines
            # ----------------------
            # low_stock_meds = await self.db_manager.read(RetailerInventory, {"RetailerId": retailer_id})
            # low_stock_list = [
            #     {
            #         "MedicineName": m.MedicineName,
            #         "MinStock": m.MinStock,
            #         "Stock": m.Quantity,
            #         "ExpiryDate": m.ExpiryDate.strftime("%d-%m-%Y")
            #     }
            #     for m in low_stock_meds if m.Quantity < m.MinStock
            # ]

            low_stock_list = []

            return {
                "TodaySales": today_sales,
                "NewOrders": new_orders_count,
                "LowStockCount": len(low_stock_list),
                "NewOrdersList": new_orders_list,
                "RecentOrders": recent_orders_list,
                "LowStock": low_stock_list
            }

        finally:
            await self.db_manager.disconnect()
