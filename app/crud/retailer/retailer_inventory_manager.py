from typing import Optional, List
from datetime import datetime
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_inventory_model import RetailerInventory

logger = get_logger(__name__)

class RetailerInventoryManager:
    """Production-ready manager for retailer inventory with full multi-retailer support."""

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
    # Combined summary + item list
    # -------------------------------------------------------------
    async def get_inventory_with_summary(self, retailer_id: int) -> dict:
        try:
            await self.db_manager.connect()
            query = {"RetailerId": retailer_id}
            all_items = await self.db_manager.read(RetailerInventory, query)

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
            logger.error(f"❌ Error fetching inventory summary for retailer {retailer_id}: {e}")
            return {"success": False, "message": f"Error fetching inventory summary: {e}"}
        finally:
            await self.db_manager.disconnect()

    # -------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------
    async def create_inventory(self, data: dict) -> dict:
        try:
            await self.db_manager.connect()
            data["Status"] = self._calculate_status(data["Quantity"], data.get("MinStock"))
            obj = await self.db_manager.create(RetailerInventory, data)
            logger.info(f"✅ Created inventory {obj.RetailerInventoryId} for retailer {data['RetailerId']}")
            return {"success": True, "message": "Inventory item created successfully", "RetailerInventoryId": obj.RetailerInventoryId}
        except Exception as e:
            logger.error(f"❌ Error creating inventory: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def get_inventory(self, retailer_id: int, retailer_inventory_id: int) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(RetailerInventory, {"RetailerInventoryId": retailer_inventory_id, "RetailerId": retailer_id})
            if not result:
                return {"success": False, "message": "Inventory not found"}
            return result[0]
        except Exception as e:
            logger.error(f"❌ Error fetching inventory {retailer_inventory_id}: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def update_inventory(self, retailer_id: int, retailer_inventory_id: int, data: dict) -> dict:
        try:
            await self.db_manager.connect()
            existing = await self.db_manager.read(RetailerInventory, {"RetailerInventoryId": retailer_inventory_id, "RetailerId": retailer_id})
            if not existing:
                return {"success": False, "message": "Inventory not found"}

            inv = existing[0]
            new_quantity = data.get("Quantity", inv.Quantity)
            new_min = data.get("MinStock", inv.MinStock)
            data["Status"] = self._calculate_status(new_quantity, new_min)

            rows = await self.db_manager.update(RetailerInventory, {"RetailerInventoryId": retailer_inventory_id, "RetailerId": retailer_id}, data)
            return {"success": True, "message": "Inventory updated", "rows_affected": rows}
        except Exception as e:
            logger.error(f"❌ Error updating inventory: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def delete_inventory(self, retailer_id: int, retailer_inventory_id: int) -> dict:
        try:
            await self.db_manager.connect()
            rows = await self.db_manager.delete(RetailerInventory, {"RetailerInventoryId": retailer_inventory_id, "RetailerId": retailer_id})
            if rows:
                return {"success": True, "message": "Inventory deleted", "rows_affected": rows}
            return {"success": False, "message": "Inventory not found"}
        except Exception as e:
            logger.error(f"❌ Error deleting inventory: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    # -------------------------------------------------------------
    # Business Logic
    # -------------------------------------------------------------
    async def reduce_stock_after_order(self, retailer_id: int, retailer_inventory_id: int, quantity_ordered: int) -> dict:
        try:
            await self.db_manager.connect()
            items = await self.db_manager.read(RetailerInventory, {"RetailerInventoryId": retailer_inventory_id, "RetailerId": retailer_id})
            if not items:
                return {"success": False, "message": "Item not found"}

            item = items[0]
            if (item.Quantity or 0) < quantity_ordered:
                return {"success": False, "message": "Insufficient stock"}

            new_quantity = max(0, (item.Quantity or 0) - quantity_ordered)
            new_status = self._calculate_status(new_quantity, item.MinStock)

            await self.db_manager.update(
                RetailerInventory,
                {"RetailerInventoryId": retailer_inventory_id},
                {"Quantity": new_quantity, "Status": new_status}
            )

            logger.info(f"📦 Reduced stock for {item.MedicineName}: {item.Quantity} → {new_quantity}")
            return {"success": True, "message": "Stock reduced", "NewQuantity": new_quantity, "Status": new_status}
        except Exception as e:
            logger.error(f"❌ Error reducing stock: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def increase_stock_after_return(self, retailer_id: int, retailer_inventory_id: int, quantity_returned: int) -> dict:
        try:
            await self.db_manager.connect()
            items = await self.db_manager.read(RetailerInventory, {"RetailerInventoryId": retailer_inventory_id, "RetailerId": retailer_id})
            if not items:
                return {"success": False, "message": "Item not found"}

            item = items[0]
            new_quantity = (item.Quantity or 0) + quantity_returned
            new_status = self._calculate_status(new_quantity, item.MinStock)

            await self.db_manager.update(
                RetailerInventory,
                {"RetailerInventoryId": retailer_inventory_id},
                {"Quantity": new_quantity, "Status": new_status}
            )

            logger.info(f"🔁 Increased stock for {item.MedicineName}: {item.Quantity} → {new_quantity}")
            return {"success": True, "message": "Stock increased", "NewQuantity": new_quantity, "Status": new_status}
        except Exception as e:
            logger.error(f"❌ Error increasing stock: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def add_stock_from_distributor(self, retailer_id: int, retailer_inventory_id: int, quantity_received: int) -> dict:
        try:
            await self.db_manager.connect()
            items = await self.db_manager.read(RetailerInventory, {"RetailerInventoryId": retailer_inventory_id, "RetailerId": retailer_id})
            if not items:
                return {"success": False, "message": "Item not found"}

            item = items[0]
            new_quantity = (item.Quantity or 0) + quantity_received
            new_status = self._calculate_status(new_quantity, item.MinStock)

            await self.db_manager.update(
                RetailerInventory,
                {"RetailerInventoryId": retailer_inventory_id},
                {"Quantity": new_quantity, "Status": new_status}
            )

            logger.info(f"🚚 Distributor stock added for {item.MedicineName}: +{quantity_received}")
            return {"success": True, "message": "Distributor stock added", "NewQuantity": new_quantity, "Status": new_status}
        except Exception as e:
            logger.error(f"❌ Error adding distributor stock: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def mark_expired_stock(self, retailer_id: Optional[int] = None) -> dict:
        """Mark expired items as out of stock."""
        try:
            await self.db_manager.connect()
            query = {"RetailerId": retailer_id} if retailer_id else None
            all_items = await self.db_manager.read(RetailerInventory, query)

            expired_items = [i for i in all_items if i.ExpiryDate and i.ExpiryDate < datetime.now().date()]
            count = 0
            for i in expired_items:
                await self.db_manager.update(
                    RetailerInventory,
                    {"RetailerInventoryId": i.RetailerInventoryId},
                    {"Quantity": 0, "Status": "no"}
                )
                count += 1

            logger.info(f"⚠️ Marked {count} items expired for retailer {retailer_id or 'ALL'}.")
            return {"success": True, "message": f"Marked {count} expired items"}
        except Exception as e:
            logger.error(f"❌ Error marking expired stock: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()
