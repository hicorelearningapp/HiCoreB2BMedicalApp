from typing import Dict
from datetime import datetime
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_order_model import RetailerOrder
from ...models.retailer.retailer_model import Retailer


class DistributorDashboardManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def get_dashboard(self, distributor_id: int) -> Dict:
        await self.db_manager.connect()

        try:
            today = datetime.today().date()

            # Fetch all orders for the distributor
            orders = await self.db_manager.read(
                RetailerOrder, {"DistributorId": distributor_id}
            )

            orders_today = [o for o in orders if o.OrderDateTime.date() == today]
            new_orders = [o for o in orders_today if o.OrderStage == "New"]

            # Fetch all retailers for the distributor
            # This avoids passing lists to SQLite
            retailers = await self.db_manager.read(
                Retailer, {}
            )

            # Map RetailerId -> RetailerName
            retailer_map = {r.RetailerId: r.OwnerName for r in retailers}

            return {
                "TodaySales": sum(o.Amount for o in orders_today),
                "NewOrders": len(new_orders),
                "NewOrdersList": [
                    {
                        "OrderID": o.OrderId,
                        "RetailerName": retailer_map.get(o.RetailerId, "Unknown"),
                        "Price": o.Amount
                    }
                    for o in new_orders
                ],
                "RecentOrders": [
                    {
                        "OrderID": o.OrderId,
                        "RetailerName": retailer_map.get(o.RetailerId, "Unknown"),
                        "Price": o.Amount,
                        "Status": o.OrderStatus
                    }
                    for o in orders
                ]
            }

        finally:
            await self.db_manager.disconnect()
