from fastapi import APIRouter, HTTPException
from typing import List
from ...config import settings
from ...schemas.retailer.retailer_inventory_schema import RetailerInventoryCreate, RetailerInventoryUpdate
from ...crud.retailer.retailer_inventory_manager import RetailerInventoryManager
from ...utils.logger import get_logger

logger = get_logger(__name__)

class RetailerInventoryAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = RetailerInventoryManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        # CRUD routes
        self.router.post("/{retailer_id}/inventory")(self.create_inventory)
        self.router.get("/{retailer_id}/inventory")(self.get_all_inventory)
        self.router.get("/{retailer_id}/inventory/{inventory_id}")(self.get_inventory)
        self.router.put("/{retailer_id}/inventory/{inventory_id}")(self.update_inventory)
        self.router.delete("/{retailer_id}/inventory/{inventory_id}")(self.delete_inventory)

        # Additional business routes
        self.router.post("/{retailer_id}/inventory/{inventory_id}/reduce")(self.reduce_stock_after_order)
        self.router.post("/{retailer_id}/inventory/{inventory_id}/increase")(self.increase_stock_after_return)
        self.router.post("/{retailer_id}/inventory/{inventory_id}/add_from_distributor")(self.add_stock_from_distributor)
        self.router.post("/{retailer_id}/inventory/mark_expired")(self.mark_expired_stock)

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------
    async def create_inventory(self, retailer_id: int, inventory: RetailerInventoryCreate):
        try:
            inventory.RetailerId = retailer_id
            return await self.crud.create_inventory(inventory.dict())
        except Exception as e:
            logger.error(f"❌ Error creating inventory for retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_inventory(self, retailer_id: int, inventory_id: int):
        try:
            result = await self.crud.get_inventory(retailer_id, inventory_id)
            if not result:
                raise HTTPException(status_code=404, detail="Inventory not found")
            return result
        except Exception as e:
            logger.error(f"❌ Error fetching inventory {inventory_id} for retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_inventory(self, retailer_id: int):
        try:
            return await self.crud.get_inventory_with_summary(retailer_id)
        except Exception as e:
            logger.error(f"❌ Error fetching inventory for retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_inventory(self, retailer_id: int, inventory_id: int, inventory: RetailerInventoryUpdate):
        try:
            return await self.crud.update_inventory(retailer_id, inventory_id, inventory.dict(exclude_unset=True))
        except Exception as e:
            logger.error(f"❌ Error updating inventory {inventory_id} for retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_inventory(self, retailer_id: int, inventory_id: int):
        try:
            return await self.crud.delete_inventory(retailer_id, inventory_id)
        except Exception as e:
            logger.error(f"❌ Error deleting inventory {inventory_id} for retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------------
    # Additional Business Operations
    # ------------------------------------------------------------------
    async def reduce_stock_after_order(self, retailer_id: int, inventory_id: int, quantity: int):
        try:
            return await self.crud.reduce_stock_after_order(retailer_id, inventory_id, quantity)
        except Exception as e:
            logger.error(f"❌ Error reducing stock for item {inventory_id}, retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def increase_stock_after_return(self, retailer_id: int, inventory_id: int, quantity: int):
        try:
            return await self.crud.increase_stock_after_return(retailer_id, inventory_id, quantity)
        except Exception as e:
            logger.error(f"❌ Error increasing stock for item {inventory_id}, retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def add_stock_from_distributor(self, retailer_id: int, inventory_id: int, quantity: int):
        try:
            return await self.crud.add_stock_from_distributor(retailer_id, inventory_id, quantity)
        except Exception as e:
            logger.error(f"❌ Error adding distributor stock for item {inventory_id}, retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def mark_expired_stock(self, retailer_id: int):
        try:
            return await self.crud.mark_expired_stock(retailer_id)
        except Exception as e:
            logger.error(f"❌ Error marking expired stock for retailer {retailer_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
