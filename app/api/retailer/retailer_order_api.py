from fastapi import APIRouter, HTTPException
from typing import Optional
from ...config import settings
from ...schemas.retailer.retailer_order_schema import (
    RetailerOrderCreate,
    RetailerOrderUpdate,
)
from ...crud.retailer.retailer_order_manager import RetailerOrderManager
from ...schemas.retailer.retailer_order_schema import (
    RetailerOrderItemCreate,
    RetailerOrderItemUpdate,
)
from ...crud.retailer.retailer_order_manager import RetailerOrderItemManager



class RetailerOrderAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = RetailerOrderManager(settings.db_type)
        self.register()

    def register(self):
        self.router.post("/retailer-orders")(self.create)
        self.router.get("/retailer-orders/{order_id}")(self.get)
        self.router.get("/retailer-orders/retailer/{retailer_id}")(self.get_by_retailer)
        self.router.put("/retailer-orders/{order_id}")(self.update)
        self.router.delete("/retailer-orders/{order_id}")(self.delete)

    async def create(self, data: RetailerOrderCreate):
        return await self.manager.create_order(data)

    async def get(self, order_id: int):
        return await self.manager.get_order(order_id)

    async def get_by_retailer(self, retailer_id: Optional[int] = None):
        return await self.manager.get_orders_by_retailer(retailer_id)

    async def update(self, order_id: int, data: RetailerOrderUpdate):
        return await self.manager.update_order(order_id, data)

    async def delete(self, order_id: int):
        return await self.manager.delete_order(order_id)




class RetailerOrderItemAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = RetailerOrderItemManager(settings.db_type)
        self.register()

    def register(self):
        self.router.post("/retailer-order-items")(self.create)
        self.router.get("/retailer-order-items/order/{order_id}")(self.get_by_order)
        self.router.put("/retailer-order-items/{item_id}")(self.update)
        self.router.delete("/retailer-order-items/{item_id}")(self.delete)

    async def create(self, data: RetailerOrderItemCreate):
        return await self.manager.create_item(data)

    async def get_by_order(self, order_id: int):
        return await self.manager.get_items_by_order(order_id)

    async def update(self, item_id: int, data: RetailerOrderItemUpdate):
        return await self.manager.update_item(item_id, data)

    async def delete(self, item_id: int):
        return await self.manager.delete_item(item_id)
