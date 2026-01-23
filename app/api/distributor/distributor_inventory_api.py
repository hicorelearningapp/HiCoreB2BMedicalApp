from fastapi import APIRouter, HTTPException
from ...config import settings
from ...schemas.distributor.distributor_inventory_schema import DistributorInventoryCreate, DistributorInventoryUpdate
from ...crud.distributor.distributor_inventory_manager import DistributorInventoryManager

class DistributorInventoryAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = DistributorInventoryManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/{distributor_id}/inventory")(self.create_inventory)
        self.router.get("/{distributor_id}/inventory")(self.get_all_inventory)
        self.router.get("/{distributor_id}/inventory/{inventory_id}")(self.get_inventory)
        self.router.put("/{distributor_id}/inventory/{inventory_id}")(self.update_inventory)
        self.router.delete("/{distributor_id}/inventory/{inventory_id}")(self.delete_inventory)

        # business
        self.router.post("/{distributor_id}/inventory/{inventory_id}/reduce")(self.reduce_stock)
        self.router.post("/{distributor_id}/inventory/{inventory_id}/increase")(self.add_stock)

    async def create_inventory(self, distributor_id: int, inventory: DistributorInventoryCreate):
        try:
            inventory.DistributorId = distributor_id
            return await self.crud.create_inventory(inventory.dict())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_inventory(self, distributor_id: int, inventory_id: int):
        result = await self.crud.get_inventory(distributor_id, inventory_id)
        if not result:
            raise HTTPException(404, "Inventory not found")
        return result

    async def get_all_inventory(self, distributor_id: int):
        return await self.crud.get_inventory_with_summary(distributor_id)

    async def update_inventory(self, distributor_id: int, inventory_id: int, data: DistributorInventoryUpdate):
        return await self.crud.update_inventory(distributor_id, inventory_id, data.dict(exclude_unset=True))

    async def delete_inventory(self, distributor_id: int, inventory_id: int):
        return await self.crud.delete_inventory(distributor_id, inventory_id)

    async def reduce_stock(self, distributor_id: int, inventory_id: int, qty: int):
        return await self.crud.reduce_stock(distributor_id, inventory_id, qty)

    async def add_stock(self, distributor_id: int, inventory_id: int, qty: int):
        return await self.crud.add_stock(distributor_id, inventory_id, qty)
