from fastapi import APIRouter, HTTPException
from typing import Optional
from ...config import settings
from ...schemas.distributor.pharma_order_schema import PharmaOrderCreate, PharmaOrderUpdate
from ...crud.distributor.pharma_order_manager import PharmaOrderManager


class PharmaOrderAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = PharmaOrderManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/pharma-orders")(self.create_order)
        self.router.get("/pharma-orders/{po_number}")(self.get_order)
        self.router.get("/{distributor_id}/pharma-orders")(self.get_all_orders)
        self.router.put("/pharma-orders/{po_number}")(self.update_order)
        self.router.delete("/pharma-orders/{po_number}")(self.delete_order)

    # -----------------------------
    # Create Order
    # -----------------------------
    async def create_order(self, order: PharmaOrderCreate):
        try:
            return await self.crud.create_order(order)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Get Order by PO Number
    # -----------------------------
    async def get_order(self, po_number: int):
        try:
            return await self.crud.get_order(po_number)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Get All Orders (optional by distributor)
    # -----------------------------
    async def get_all_orders(self, distributor_id: Optional[int] = None):
        try:
            return await self.crud.get_all_orders(distributor_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Update Order
    # -----------------------------
    async def update_order(self, po_number: int, data: PharmaOrderUpdate):
        try:
            return await self.crud.update_order(po_number, data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Delete Order
    # -----------------------------
    async def delete_order(self, po_number: int):
        try:
            return await self.crud.delete_order(po_number)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
