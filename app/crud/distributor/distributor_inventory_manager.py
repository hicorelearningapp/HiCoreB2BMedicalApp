from typing import Optional, List
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.distributor.distributor_inventory_model import DistributorInventory

logger = get_logger(__name__)

class DistributorInventoryManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    # -------------------------------------------------------------
    # Utility: Calculate stock status
    # -------------------------------------------------------------
    def _calculate_status(self, quantity: int, min_stock: Optional[int]) -> str:
        min_stock = min_stock or 0
        if quantity == 0:
            return "no"
        elif quantity <= min_stock:
            return "low"
        return "in"

    # -------------------------------------------------------------
    # Combined summary + list
    # -------------------------------------------------------------
    async def get_inventory_with_summary(self, distributor_id: int) -> dict:
        try:
            await self.db_manager.connect()
            query = {"DistributorId": distributor_id}
            all_items = await self.db_manager.read(DistributorInventory, query)

            total = len(all_items)
            no_stock = sum(1 for i in all_items if (i.Quantity or 0) == 0)
            low_stock = sum(1 for i in all_items if 0 < (i.Quantity or 0) <= (i.MinStock or 0))
            in_stock = sum(1 for i in all_items if (i.Quantity or 0) > (i.MinStock or 0))

            return {
                "TotalItems": total,
                "InStock": in_stock,
                "LowStock": low_stock,
                "NoStock": no_stock,
                "Items": all_items
            }

        except Exception as e:
            logger.error(f"❌ Error fetching inventory summary for distributor {distributor_id}: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    # -------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------
    async def create_inventory(self, data: dict) -> dict:
        try:
            await self.db_manager.connect()
            data["Status"] = self._calculate_status(data["Quantity"], data.get("MinStock"))
            obj = await self.db_manager.create(DistributorInventory, data)

            logger.info(f"✅ Created DistributorInventory {obj.DistributorInventoryId}")
            return {"success": True, "DistributorInventoryId": obj.DistributorInventoryId}
        except Exception as e:
            logger.error(f"❌ Error creating distributor inventory: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def get_inventory(self, distributor_id: int, inventory_id: int):
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id, "DistributorId": distributor_id}
            )
            if not result:
                return {"success": False, "message": "Inventory not found"}
            return result[0]

        except Exception as e:
            logger.error(f"❌ Error fetching distributor inventory: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def update_inventory(self, distributor_id: int, inventory_id: int, data: dict):
        try:
            await self.db_manager.connect()
            existing = await self.db_manager.read(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id, "DistributorId": distributor_id}
            )

            if not existing:
                return {"success": False, "message": "Inventory not found"}

            inv = existing[0]
            q = data.get("Quantity", inv.Quantity)
            m = data.get("MinStock", inv.MinStock)

            data["Status"] = self._calculate_status(q, m)

            rows = await self.db_manager.update(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id, "DistributorId": distributor_id},
                data,
            )

            return {"success": True, "rows_affected": rows}

        except Exception as e:
            logger.error(f"❌ Error updating distributor inventory: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def delete_inventory(self, distributor_id: int, inventory_id: int):
        try:
            await self.db_manager.connect()
            rows = await self.db_manager.delete(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id, "DistributorId": distributor_id},
            )

            if rows:
                return {"success": True, "rows_affected": rows}
            return {"success": False, "message": "Inventory not found"}

        except Exception as e:
            logger.error(f"❌ Error deleting distributor inventory: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    # -------------------------------------------------------------
    # Stock business logic
    # -------------------------------------------------------------
    async def reduce_stock(self, distributor_id: int, inventory_id: int, qty: int):
        try:
            await self.db_manager.connect()
            items = await self.db_manager.read(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id, "DistributorId": distributor_id},
            )

            if not items:
                return {"success": False, "message": "Item not found"}

            item = items[0]
            if item.Quantity < qty:
                return {"success": False, "message": "Not enough stock"}

            new_qty = item.Quantity - qty
            new_status = self._calculate_status(new_qty, item.MinStock)

            await self.db_manager.update(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id},
                {"Quantity": new_qty, "Status": new_status},
            )

            return {"success": True, "NewQuantity": new_qty}

        except Exception as e:
            logger.error(f"❌ Error reducing distributor stock: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def add_stock(self, distributor_id: int, inventory_id: int, qty: int):
        try:
            await self.db_manager.connect()
            items = await self.db_manager.read(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id, "DistributorId": distributor_id},
            )

            if not items:
                return {"success": False, "message": "Item not found"}

            item = items[0]
            new_qty = item.Quantity + qty
            new_status = self._calculate_status(new_qty, item.MinStock)

            await self.db_manager.update(
                DistributorInventory,
                {"DistributorInventoryId": inventory_id},
                {"Quantity": new_qty, "Status": new_status},
            )

            return {"success": True, "NewQuantity": new_qty}

        except Exception as e:
            logger.error(f"❌ Error increasing distributor stock: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()
