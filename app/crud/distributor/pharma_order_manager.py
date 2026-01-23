from typing import List, Optional
from ...utils.timezone import ist_now
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.distributor.pharma_order_model import PharmaOrder, PharmaOrderItem
from ...schemas.distributor.pharma_order_schema import (
    PharmaOrderCreate,
    PharmaOrderUpdate,
    PharmaOrderRead,
)

logger = get_logger(__name__)


class PharmaOrderManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    # ------------------------------------------------------------
    # 🟢 Create Order
    # ------------------------------------------------------------
    async def create_order(self, order: PharmaOrderCreate) -> dict:
        try:
            await self.db_manager.connect()

            # Step 1: Create PharmaOrder
            order_data = order.dict(exclude={"Items"})
            order_data["OrderDate"] = ist_now()
            new_order = await self.db_manager.create(PharmaOrder, order_data)
            po_number = new_order.PONumber

            # Step 2: Create order items
            for item in order.Items:
                item_data = item.dict()
                item_data["PONumber"] = po_number
                item_data["TotalAmount"] = (item.Price or 0) * (item.Quantity or 0)
                await self.db_manager.create(PharmaOrderItem, item_data)

            logger.info(f"✅ Pharma Order {po_number} created successfully")
            return {"success": True, "message": "Order created successfully", "PONumber": po_number}

        except Exception as e:
            logger.error(f"❌ Error creating order: {e}")
            return {"success": False, "message": f"Error creating order: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟡 Get Order by PO Number
    # ------------------------------------------------------------
    async def get_order(self, po_number: int) -> dict:
        try:
            await self.db_manager.connect()
            orders = await self.db_manager.read(PharmaOrder, {"PONumber": po_number})
            if not orders:
                return {"success": False, "message": "Order not found"}

            order = orders[0]
            items = await self.db_manager.read(PharmaOrderItem, {"PONumber": po_number})
            order_schema = PharmaOrderRead.from_orm(order).dict()
            order_schema["Items"] = [item.__dict__ for item in items]

            return order_schema

        except Exception as e:
            logger.error(f"❌ Error fetching order {po_number}: {e}")
            return {"success": False, "message": f"Error fetching order: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟢 Get All Orders (optional filter by distributor)
    # ------------------------------------------------------------
    async def get_all_orders(self, distributor_id: Optional[int] = None) -> List[dict]:
        try:
            await self.db_manager.connect()
            query = {"DistributorId": distributor_id} if distributor_id else None
            result = await self.db_manager.read(PharmaOrder, query)
            orders = [PharmaOrderRead.from_orm(o).dict() for o in result]
            return orders
        except Exception as e:
            logger.error(f"❌ Error fetching orders: {e}")
            return {"success": False, "message": f"Error fetching orders: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟠 Update Order
    # ------------------------------------------------------------
    async def update_order(self, po_number: int, data: PharmaOrderUpdate) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.update(
                PharmaOrder, {"PONumber": po_number}, data.dict(exclude_unset=True)
            )
            if rowcount:
                logger.info(f"✅ Updated Pharma Order {po_number}")
                return {"success": True, "message": "Order updated successfully"}
            return {"success": False, "message": "Order not found or no changes made"}
        except Exception as e:
            logger.error(f"❌ Error updating order {po_number}: {e}")
            return {"success": False, "message": f"Error updating order: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🔴 Delete Order
    # ------------------------------------------------------------
    async def delete_order(self, po_number: int) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.delete(PharmaOrder, {"PONumber": po_number})
            if rowcount:
                logger.info(f"🗑️ Deleted Pharma Order {po_number}")
                return {"success": True, "message": "Order deleted successfully"}
            return {"success": False, "message": "Order not found"}
        except Exception as e:
            logger.error(f"❌ Error deleting order {po_number}: {e}")
            return {"success": False, "message": f"Error deleting order: {e}"}
        finally:
            await self.db_manager.disconnect()
