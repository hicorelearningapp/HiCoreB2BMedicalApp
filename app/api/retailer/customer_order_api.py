from fastapi import APIRouter, HTTPException
from ...crud.retailer.customer_order_manager import CustomerOrderManager

router = APIRouter()


class CustomerOrderAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = CustomerOrderManager()
        self.register_routes()

    def register_routes(self):
        self.router.get("/retailer/dashboard/{retailer_id}")(self.get_dashboard)
        self.router.get("/retailer/sales-dashboard/{retailer_id}")(self.sales_dashboard)
        self.router.get("/retailer/get_all_orders/{retailer_id}")(self.get_all_orders)
        self.router.get("/retailer/get_order/{order_id}")(self.get_order)
        self.router.patch("/retailer/update_order_status/{order_id}")(self.update_order_status)

    async def update_order_status(self, order_id: int, status: str):
        try:
            return await self.manager.update_order_status(order_id, status)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_order(self, order_id: int):
        try:
            return await self.manager.get_order(order_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_orders(self, retailer_id: int):
        try:
            return await self.manager.get_all_orders(retailer_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def sales_dashboard(self, retailer_id: int):
        try:
            return await self.manager.sales_dashboard(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    async def get_dashboard(self, retailer_id: int):
        try:
            return await self.manager.get_dashboard(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
