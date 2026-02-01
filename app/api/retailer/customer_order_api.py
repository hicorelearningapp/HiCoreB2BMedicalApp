# app/api/retailer/order_api.py

# @router.get("/get_orders/{retailer_id}", tags=["Customer orders"])
# async def get_orders(retailer_id: int):
#     """
#     Fetch orders from external API by retailer_id
#     and return aggregated order statistics
#     """
#     url = f"{GET_ORDER_BASE_URL}{retailer_id}"

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, timeout=10.0)
#             response.raise_for_status()
#             orders = response.json()  # <-- list of orders

#         except httpx.HTTPStatusError as exc:
#             raise HTTPException(
#                 status_code=exc.response.status_code,
#                 detail=f"Error fetching orders: {exc.response.text}"
#             )
#         except httpx.RequestError as exc:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Request failed: {exc}"
#             )

#     # ---- calculations ----
#     total_orders = len(orders)

#     delivered = sum(1 for o in orders if o.get("Status") == "Delivered")
#     cancelled = sum(1 for o in orders if o.get("Status") == "Cancelled")
#     in_transit = sum(1 for o in orders if o.get("Status") == "InTransit")
#     pending = sum(1 for o in orders if o.get("Status") == "Pending")
#     new = sum(1 for o in orders if o.get("Status") == "New")

#     accepted = sum(
#         1 for o in orders
#         if o.get("Status") not in ("New", "Cancelled")
#     )

#     new_orders = [o for o in orders if o.get("Status") == "New"]

#     # ---- final response ----
#     return {
#         "TotalOrders": total_orders,
#         "New": new,
#         "Accepted": accepted,
#         "Pending": pending,
#         "InTransit": in_transit,
#         "Delivered": delivered,
#         "Cancelled": cancelled,
#         "NewOrders": new_orders,
#         "AllOrders": orders
#     }



# @router.patch("/update_order_status/{order_id}", tags=["Customer orders"])
# async def update_order_status(order_id: int, status: str):
#     """
#     Update order status by order_id (PATCH)
#     """
#     url = f"{UPDATE_STATUS_BASE_URL}/{order_id}/status"
#     params = {"status": status}

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.patch(url, params=params, timeout=10.0)
#             response.raise_for_status()
#         except httpx.HTTPStatusError as exc:
#             raise HTTPException(
#                 status_code=exc.response.status_code,
#                 detail=f"Error updating order status: {exc.response.text}"
#             )
#         except httpx.RequestError as exc:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Request failed: {exc}"
#             )

#     return response.json()


from fastapi import APIRouter, HTTPException
import httpx
from collections import defaultdict
import calendar
from ...crud.retailer.customer_order_manager import CustomerOrderManager

router = APIRouter()


class CustomerOrderAPI:
    def __init__(self):
        self.router = APIRouter()
        self.manager = CustomerOrderManager()
        self.register_routes()

    def register_routes(self):
        self.router.get("/retailer/sales-dashboard/{retailer_id}")(self.sales_dashboard)
        self.router.get("/get_orders/{retailer_id}")(self.get_orders)
        self.router.patch("/update_order_status/{order_id}")(self.update_order_status)

    async def update_order_status(self, order_id: int, status: str):
        try:
            return await self.manager.update_order_status(order_id, status)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_orders(self, retailer_id: int):
        try:
            return await self.manager.get_orders(retailer_id)
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
