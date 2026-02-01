from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime
from collections import defaultdict
import calendar


GET_ORDER_BASE_URL = "http://151.185.41.194:8000/orders/retailer/"
GET_ORDER_ITEM_BASE_URL = "http://151.185.41.194:8000/orders/items/retailer/"
UPDATE_STATUS_BASE_URL = "http://151.185.41.194:8000/orders"



class CustomerOrderManager:
    
    # -----------------------------
    # Update Order Status
    # -----------------------------
    async def update_order_status(self, order_id: int, status: str):
        """
        Update order status by order_id
        """
        url = f"{UPDATE_STATUS_BASE_URL}/{order_id}/status"
        params = {"status": status}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Error updating order status: {exc.response.text}"
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"Request failed: {exc}"
                )
            
    # -----------------------------
    # Get Orders by Retailer
    # -----------------------------
    async def get_orders(self, retailer_id: int):
        """
        Fetch orders from external API by retailer_id
        and return aggregated order statistics
        """
        url = f"{GET_ORDER_BASE_URL}{retailer_id}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                orders = response.json()

            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Error fetching orders: {exc.response.text}"
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"Request failed: {exc}"
                )

        # -----------------------------
        # Order Calculations
        # -----------------------------
        total_orders = len(orders)

        delivered = sum(1 for o in orders if o.get("Status") == "Delivered")
        cancelled = sum(1 for o in orders if o.get("Status") == "Cancelled")
        in_transit = sum(1 for o in orders if o.get("Status") == "InTransit")
        pending = sum(1 for o in orders if o.get("Status") == "Pending")
        new = sum(1 for o in orders if o.get("Status") == "New")

        accepted = sum(
            1 for o in orders
            if o.get("Status") not in ("New", "Cancelled")
        )

        new_orders = [o for o in orders if o.get("Status") == "New"]

        # -----------------------------
        # Final Response
        # -----------------------------
        return {
            "TotalOrders": total_orders,
            "New": new,
            "Accepted": accepted,
            "Pending": pending,
            "InTransit": in_transit,
            "Delivered": delivered,
            "Cancelled": cancelled,
            "NewOrders": new_orders,
            "AllOrders": orders
        }

    # -----------------------------
    # Retailer Sales Dashboard
    # -----------------------------
    async def sales_dashboard(self, retailer_id: int):
        try:
            async with httpx.AsyncClient() as client:
                # ---- fetch orders ----
                orders_resp = await client.get(
                    f"{GET_ORDER_BASE_URL}{retailer_id}",
                    timeout=10.0
                )
                orders_resp.raise_for_status()
                orders = orders_resp.json()

                # ---- fetch order items ----
                items_resp = await client.get(
                    f"{GET_ORDER_ITEM_BASE_URL}{retailer_id}",
                    timeout=10.0
                )
                items_resp.raise_for_status()
                order_items = items_resp.json()

            # ---------------------------
            # Revenue & Orders
            # ---------------------------
            total_revenue = sum(o.get("TotalAmount", 0) or 0 for o in orders)
            total_orders = len(orders)
            avg_order_value = (
                total_revenue / total_orders if total_orders > 0 else 0
            )

            # ---------------------------
            # Monthly Trends
            # ---------------------------
            sales_trend_dict = defaultdict(float)
            order_volume_dict = defaultdict(int)

            for o in orders:
                if o.get("OrderDateTime"):
                    month = o["OrderDateTime"][5:7]  # YYYY-MM-DD
                    month_name = calendar.month_abbr[int(month)]
                    sales_trend_dict[month_name] += o.get("TotalAmount", 0) or 0
                    order_volume_dict[month_name] += 1

            all_months = [calendar.month_abbr[i] for i in range(1, 13)]
            sales_trend = [{m: sales_trend_dict.get(m, 0)} for m in all_months]
            order_volume = [{m: order_volume_dict.get(m, 0)} for m in all_months]

            # ---------------------------
            # Top Selling Products
            # ---------------------------
            # product_sales = defaultdict(lambda: {"Quantity": 0, "UnitPrice": 0})

            # for item in order_items:
            #     name = item.get("MedicineName")
            #     qty = item.get("Quantity", 0) or 0
            #     price = item.get("UnitPrice", 0) or 0

            #     product_sales[name]["Quantity"] += qty
            #     product_sales[name]["UnitPrice"] += qty * price

            # top_products = sorted(
            #     [
            #         {
            #             "MedicineName": k,
            #             "Quantity": v["Quantity"],
            #             "UnitPrice": v["UnitPrice"]
            #         }
            #         for k, v in product_sales.items()
            #     ],
            #     key=lambda x: x["Quantity"],
            #     reverse=True
            # )[:10]

            # ---------------------------
            # Final Response
            # ---------------------------
            return {
                "TotalRevenue": total_revenue,
                "TotalOrders": total_orders,
                "AvgOrderValue": avg_order_value,
                "SalesTrend": sales_trend,
                "OrderVolume": order_volume
                # "TopSellingProduct": top_products
            }

        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    # -----------------------------
    # Retailer Dashboard
    # -----------------------------
    async def get_dashboard(self, retailer_id: int):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GET_ORDER_BASE_URL}{retailer_id}",
                    timeout=10.0
                )
                response.raise_for_status()
                orders = response.json()

            today = datetime.today().date()

            # ----------------------
            # Today's Orders
            # ----------------------
            orders_today = [
                o for o in orders
                if o.get("OrderDateTime")
                and datetime.fromisoformat(o["OrderDateTime"]).date() == today
            ]

            today_sales = sum(o.get("TotalAmount", 0) or 0 for o in orders_today)

            new_orders_today = [
                o for o in orders_today if o.get("Status") == "New"
            ]

            # ----------------------
            # New Orders List
            # ----------------------
            new_orders_list = [
                {
                    "OrderID": o.get("OrderId"),
                    "CustomerName": o.get("CustomerName"),
                    "Price": o.get("TotalAmount")
                }
                for o in new_orders_today
            ]

            # ----------------------
            # Recent Orders List
            # ----------------------
            recent_orders_list = [
                {
                    "OrderID": o.get("OrderId"),
                    "CustomerName": o.get("CustomerName"),
                    "Price": o.get("TotalAmount"),
                    "Status": o.get("Status")
                }
                for o in orders
            ]

            # ----------------------
            # Low Stock (future API)
            # ----------------------
            low_stock_list = []

            # ----------------------
            # Final Response
            # ----------------------
            return {
                "TodaySales": today_sales,
                "NewOrders": len(new_orders_today),
                "LowStockCount": len(low_stock_list),
                "NewOrdersList": new_orders_list,
                "RecentOrders": recent_orders_list,
                "LowStock": low_stock_list
            }

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error fetching dashboard data: {exc.response.text}"
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc)
            )
