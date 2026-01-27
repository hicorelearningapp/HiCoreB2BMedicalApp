from typing import List
from ...utils.timezone import ist_now
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_order_model import (
    RetailerOrder,
    RetailerOrderItem,
)
from ...schemas.retailer.retailer_order_schema import (
    RetailerOrderCreate,
    RetailerOrderItemCreate,
)
from ...utils.logger import get_logger

logger = get_logger(__name__)


class RetailerOrderManager:
    def __init__(self, db_type: str):
        self.db = DatabaseManager(db_type)

    # ---------------------------------------------------
    # Create Order
    # ---------------------------------------------------
    async def create_order(
        self,
        order_data: RetailerOrderCreate,
        items: List[RetailerOrderItemCreate],
    ):
        try:
            await self.db.connect()

            total_amount = sum(i.TotalAmount for i in items)

            order_dict = order_data.model_dump()
            order_dict.update({
                "Amount": total_amount,
                "CreatedAt": ist_now(),
                "UpdatedAt": ist_now(),
            })

            order = await self.db.create(RetailerOrder, order_dict)

            for item in items:
                item_dict = item.model_dump()
                item_dict.update({
                    "OrderId": order.OrderId,
                    "RetailerId": order.RetailerId,
                    "DistributorId": order.DistributorId,
                })
                await self.db.create(RetailerOrderItem, item_dict)

            return {"success": True, "OrderId": order.OrderId}

        except Exception as e:
            logger.error(f"Create order error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Get Order by ID
    # ---------------------------------------------------
    async def get_order(self, order_id: int):
        try:
            await self.db.connect()

            orders = await self.db.read(RetailerOrder, {"OrderId": order_id})
            if not orders:
                return {"success": False, "message": "Order not found"}

            order = orders[0]
            items = await self.db.read(RetailerOrderItem, {"OrderId": order.OrderId})

            return {
                "success": True,
                "OrderId": order.OrderId,
                "RetailerId": order.RetailerId,
                "DistributorId": order.DistributorId,
                "Amount": order.Amount,
                "OrderDateTime": order.OrderDateTime,
                "ExpectedDelivery": order.ExpectedDelivery,
                "OrderStatus": order.OrderStatus,
                "DeliveryStatus": order.DeliveryStatus,
                "PaymentStatus": order.PaymentStatus,
                "Items": [
                    {
                        "ItemId": i.ItemId,
                        "MedicineId": i.MedicineId,
                        "Quantity": i.Quantity,
                        "GSTPercentage": i.GSTPercentage,
                        "TotalAmount": i.TotalAmount,
                    }
                    for i in items
                ],
            }

        except Exception as e:
            logger.error(f"Get order error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Update Order
    # ---------------------------------------------------
    async def update_order(self, order_id: int, data: dict):
        try:
            await self.db.connect()
            data["UpdatedAt"] = ist_now()
            updated = await self.db.update(
                RetailerOrder,
                {"OrderId": order_id},
                data,
            )
            if updated:
                return {"success": True, "message": "Order updated"}
            return {"success": False, "message": "Order not found"}
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Delete Order
    # ---------------------------------------------------
    async def delete_order(self, order_id: int):
        try:
            await self.db.connect()
            await self.db.delete(RetailerOrderItem, {"OrderId": order_id})
            deleted = await self.db.delete(RetailerOrder, {"OrderId": order_id})
            if deleted:
                return {"success": True, "message": "Order deleted"}
            return {"success": False, "message": "Order not found"}
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Get Orders by Retailer
    # ---------------------------------------------------
    async def get_orders_by_retailer(self, retailer_id: int):
        try:
            await self.db.connect()
            orders = await self.db.read(RetailerOrder, {"RetailerId": retailer_id})

            return {
                "TotalOrders": len(orders),
                "Orders": [
                    {
                        "OrderId": o.OrderId,
                        "DistributorId": o.DistributorId,
                        "Amount": o.Amount,
                        "OrderDateTime": o.OrderDateTime,
                        "ExpectedDelivery": o.ExpectedDelivery,
                        "OrderStatus": o.OrderStatus,
                    }
                    for o in orders
                ],
            }
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Get Orders by Distributor
    # ---------------------------------------------------
    async def get_orders_by_distributor(self, distributor_id: int):
        try:
            await self.db.connect()
            orders = await self.db.read(RetailerOrder, {"DistributorId": distributor_id})

            return {
                "TotalOrders": len(orders),
                "Orders": [
                    {
                        "OrderId": o.OrderId,
                        "RetailerId": o.RetailerId,
                        "Amount": o.Amount,
                        "OrderDateTime": o.OrderDateTime,
                        "OrderStatus": o.OrderStatus,
                    }
                    for o in orders
                ],
            }
        finally:
            await self.db.disconnect()


class RetailerOrderItemManager:
    def __init__(self, db_type: str):
        self.db = DatabaseManager(db_type)

    # ---------------------------------------------------
    # Create Item
    # ---------------------------------------------------
    async def create_item(self, data: dict):
        try:
            await self.db.connect()
            item = await self.db.create(RetailerOrderItem, data)
            return {"success": True, "ItemId": item.ItemId}
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Get Item by ID
    # ---------------------------------------------------
    async def get_item(self, item_id: int):
        try:
            await self.db.connect()
            items = await self.db.read(RetailerOrderItem, {"ItemId": item_id})
            if not items:
                return {"success": False, "message": "Item not found"}

            i = items[0]
            return {
                "success": True,
                "Item": {
                    "ItemId": i.ItemId,
                    "OrderId": i.OrderId,
                    "RetailerId": i.RetailerId,
                    "DistributorId": i.DistributorId,
                    "MedicineId": i.MedicineId,
                    "Quantity": i.Quantity,
                    "GSTPercentage": i.GSTPercentage,
                    "TotalAmount": i.TotalAmount,
                },
            }
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Get Items by Order
    # ---------------------------------------------------
    async def get_items_by_order(self, order_id: int):
        try:
            await self.db.connect()
            items = await self.db.read(RetailerOrderItem, {"OrderId": order_id})
            return {
                "success": True,
                "Items": [
                    {
                        "ItemId": i.ItemId,
                        "MedicineId": i.MedicineId,
                        "Quantity": i.Quantity,
                        "GSTPercentage": i.GSTPercentage,
                        "TotalAmount": i.TotalAmount,
                    }
                    for i in items
                ],
            }
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Update Item
    # ---------------------------------------------------
    async def update_item(self, item_id: int, data: dict):
        try:
            await self.db.connect()
            updated = await self.db.update(
                RetailerOrderItem,
                {"ItemId": item_id},
                data,
            )
            if updated:
                return {"success": True, "message": "Item updated"}
            return {"success": False, "message": "Item not found"}
        finally:
            await self.db.disconnect()

    # ---------------------------------------------------
    # Delete Item
    # ---------------------------------------------------
    async def delete_item(self, item_id: int):
        try:
            await self.db.connect()
            deleted = await self.db.delete(
                RetailerOrderItem,
                {"ItemId": item_id},
            )
            if deleted:
                return {"success": True, "message": "Item deleted"}
            return {"success": False, "message": "Item not found"}
        finally:
            await self.db.disconnect()
