from fastapi import APIRouter, HTTPException
from typing import List
from ...crud.retailer.retailer_order_manager import (
    RetailerOrderManager,
    RetailerOrderItemManager,
)
from ...schemas.retailer.retailer_order_schema import (
    RetailerOrderCreate,
    RetailerOrderItemCreate,
    RetailerOrderItemUpdate,
)
from ...config import settings



class RetailerOrderAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = RetailerOrderManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/retailer/orders")(self.create_order)
        self.router.get("/retailer/orders/{order_id}")(self.get_order)
        self.router.put("/retailer/orders/{order_id}")(self.update_order)
        self.router.delete("/retailer/orders/{order_id}")(self.delete_order)
        self.router.get("/retailer/{retailer_id}/orders")(self.get_orders_by_retailer)
        self.router.get("/distributor/{distributor_id}/orders")(self.get_orders_by_distributor)

    async def create_order(self, payload: RetailerOrderCreate):
        result = await self.crud.create_order(payload.order, payload.items)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    async def get_order(self, order_id: int):
        result = await self.crud.get_order(order_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    async def update_order(self, order_id: int, data: dict):
        result = await self.crud.update_order(order_id, data)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    async def delete_order(self, order_id: int):
        result = await self.crud.delete_order(order_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    async def get_orders_by_retailer(self, retailer_id: int):
        return await self.crud.get_orders_by_retailer(retailer_id)

    async def get_orders_by_distributor(self, distributor_id: int):
        return await self.crud.get_orders_by_distributor(distributor_id)



class RetailerOrderItemAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = RetailerOrderItemManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/retailer/order/items")(self.create_item)
        self.router.get("/retailer/order/items/{item_id}")(self.get_item)
        self.router.put("/retailer/order/items/{item_id}")(self.update_item)
        self.router.delete("/retailer/order/items/{item_id}")(self.delete_item)
        self.router.get("/retailer/orders/{order_id}/items")(self.get_items_by_order)

    async def create_item(self, item: RetailerOrderItemCreate):
        result = await self.crud.create_item(item.model_dump())
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    async def get_item(self, item_id: int):
        result = await self.crud.get_item(item_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    async def update_item(self, item_id: int, data: RetailerOrderItemUpdate):
        result = await self.crud.update_item(
            item_id,
            data.model_dump(exclude_unset=True)
        )
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    async def delete_item(self, item_id: int):
        result = await self.crud.delete_item(item_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    async def get_items_by_order(self, order_id: int):
        return await self.crud.get_items_by_order(order_id)
