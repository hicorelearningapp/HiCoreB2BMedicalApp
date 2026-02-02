from typing import Optional, Dict, Any
from ...utils.timezone import ist_now
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_order_model import RetailerOrder
from ...models.retailer.retailer_model import Retailer
from ...schemas.retailer.retailer_order_schema import (
    RetailerOrderCreate,
    RetailerOrderUpdate,
    RetailerOrderRead,
)
from ...models.retailer.retailer_order_model import RetailerOrderItem
from ...schemas.retailer.retailer_order_schema import (
    RetailerOrderItemCreate,
    RetailerOrderItemUpdate,
    RetailerOrderItemRead,
)


logger = get_logger(__name__)


class RetailerOrderManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    # ------------------------------------------------------------
    # 🟢 Create Order + Items
    # ------------------------------------------------------------
    async def create_order(self, order: RetailerOrderCreate) -> dict:
        try:
            await self.db_manager.connect()

            # ---- Create order header ----
            order_data = order.dict(exclude={"Items"})
            order_data["OrderDateTime"] = ist_now()

            new_order = await self.db_manager.create(RetailerOrder, order_data)
            order_id = new_order.OrderId

            total_items = len(order.Items)
            total_amount = 0.0

            # ---- Create items ----
            if order.Items:
                for item in order.Items:
                    item_data = item.dict()
                    item_data["OrderId"] = order_id
                    item_data["TotalAmount"] = (item.Price or 0) * (item.Quantity or 0)

                    # total_items += item.Quantity or 0
                    total_amount += item_data["TotalAmount"]

                    await self.db_manager.create(
                        RetailerOrderItem, item_data
                    )

            # ---- Update totals ----
            await self.db_manager.update(
                RetailerOrder,
                {"OrderId": order_id},
                {
                    "TotalItems": total_items,
                    "TotalAmount": total_amount,
                    "UpdatedAt": ist_now(),
                },
            )

            logger.info(f"✅ Retailer Order {order_id} created with items")

            return {
                "success": True,
                "message": "Retailer order created successfully",
                "OrderId": order_id,
            }

        except Exception as e:
            logger.error(f"❌ Error creating retailer order: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟡 Get Order + Items (Filtered Retailer Fields)
    # ------------------------------------------------------------
    async def get_order(self, order_id: int) -> dict:
        try:
            await self.db_manager.connect()

            orders = await self.db_manager.read(
                RetailerOrder, {"OrderId": order_id}
            )
            if not orders:
                return {"success": False, "message": "Order not found"}

            order = orders[0]

            items = await self.db_manager.read(
                RetailerOrderItem, {"OrderId": order_id}
            )

            # Convert order to schema
            order_schema = RetailerOrderRead.from_orm(order).dict()

            # ----------------------------
            # Fetch retailer
            # ----------------------------
            retailers = await self.db_manager.read(
                Retailer, {"RetailerId": order.RetailerId}
            )

            if retailers:
                retailer = retailers[0]
                order_schema["Retailer"] = {
                    "Name": retailer.OwnerName,
                    "ShopName": retailer.ShopName,
                    "GSTNumber": retailer.GSTNumber,
                    "LicenseNumber": retailer.LicenseNumber,
                    "AddressLine1": retailer.AddressLine1,
                    "AddressLine2": retailer.AddressLine2,
                    "City": retailer.City,
                    "State": retailer.State,
                    "Country": retailer.Country,
                    "PostalCode": retailer.PostalCode,
                    "Latitude": retailer.Latitude,
                    "Longitude": retailer.Longitude,
                    "PhoneNumber": retailer.PhoneNumber,
                    "Email": retailer.Email
                }
            else:
                order_schema["Retailer"] = None

            # ----------------------------
            # Items
            # ----------------------------
            order_schema["Items"] = [
                item.__dict__ for item in items
            ]

            return order_schema

        except Exception as e:
            logger.error(f"❌ Error fetching retailer order {order_id}: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()


    # ------------------------------------------------------------
    # 🟢 Get All Orders (filter by Retailer)
    # ------------------------------------------------------------

    async def get_orders_by_retailer(self, retailer_id: Optional[int] = None) -> Dict[str, Any]:
        try:
            await self.db_manager.connect()

            query = {"RetailerId": retailer_id} if retailer_id else None
            result = await self.db_manager.read(RetailerOrder, query)

            orders = [RetailerOrderRead.from_orm(o).dict() for o in result]

            # ---- Status counts ----
            total_orders = len(orders)

            delivered = sum(1 for o in orders if o.get("Status") == "Delivered")
            in_transit = sum(1 for o in orders if o.get("Status") == "InTransit")
            placed = sum(
                1 for o in orders
                if o.get("Status") in ("New", "Pending")
            )

            response = {
                "TotalOrders": total_orders,
                "Delivered": delivered,
                "InTransit": in_transit,
                "Placed": placed,
                "Data": orders
            }

            return response

        except Exception as e:
            logger.error(f"❌ Error fetching orders: {e}")
            return {"success": False, "message": f"Error fetching orders: {e}"}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟢 Get All Orders (filter by Distributor)
    # ------------------------------------------------------------

    async def get_orders_by_distributor(self, distributor_id: Optional[int] = None) -> Dict[str, Any]:
        try:
            await self.db_manager.connect()

            query = {"DistributorId": distributor_id} if distributor_id else None
            result = await self.db_manager.read(RetailerOrder, query)

            orders = [RetailerOrderRead.from_orm(o).dict() for o in result]

            new_orders = [await self.get_order(o.get("OrderId")) for o in orders if o.get("Status") == "New"]        

            # ---- Status counts ----
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

            response = {
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

            return response

        except Exception as e:
            logger.error(f"❌ Error fetching orders: {e}")
            return {"success": False, "message": f"Error fetching orders: {e}"}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🟠 Update Order
    # ------------------------------------------------------------
    async def update_order(self, order_id: int, data: RetailerOrderUpdate) -> dict:
        try:
            await self.db_manager.connect()

            rowcount = await self.db_manager.update(
                RetailerOrder,
                {"OrderId": order_id},
                data.dict(exclude_unset=True),
            )

            if rowcount:
                return {"success": True, "message": "Order updated"}

            return {"success": False, "message": "Order not found"}

        except Exception as e:
            logger.error(f"❌ Error updating retailer order: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    
    # ------------------------------------------------------------
    # 🔵 Update Order Status ONLY
    # ------------------------------------------------------------
    async def update_order_status(self, order_id: int, status: str) -> dict:
        try:
            await self.db_manager.connect()

            # Optional: enforce allowed status transitions
            # allowed_status = {"New", "Pending", "InTransit", "Delivered", "Cancelled"}
            # if status not in allowed_status:
            #     return {"success": False, "message": "Invalid status value"}

            rowcount = await self.db_manager.update(
                RetailerOrder,
                {"OrderId": order_id},
                {
                    "Status": status,
                    "UpdatedAt": ist_now()
                }
            )

            if rowcount:
                return {
                    "success": True,
                    "message": f"Order status updated to {status}"
                }

            return {"success": False, "message": "Order not found"}

        except Exception as e:
            logger.error(f"❌ Error updating order status: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # 🔴 Delete Order + Items
    # ------------------------------------------------------------
    async def delete_order(self, order_id: int) -> dict:
        try:
            await self.db_manager.connect()

            # delete items first
            await self.db_manager.delete(
                RetailerOrderItem, {"OrderId": order_id}
            )

            rowcount = await self.db_manager.delete(
                RetailerOrder, {"OrderId": order_id}
            )

            if rowcount:
                return {"success": True, "message": "Order deleted"}

            return {"success": False, "message": "Order not found"}

        except Exception as e:
            logger.error(f"❌ Error deleting retailer order: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()



class RetailerOrderItemManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    # ------------------------------------------------------------
    # Create Item
    # ------------------------------------------------------------
    async def create_item(self, item: RetailerOrderItemCreate) -> dict:
        try:
            await self.db_manager.connect()
            data = item.dict()
            data["TotalAmount"] = (item.Price or 0) * (item.Quantity or 0)

            new_item = await self.db_manager.create(RetailerOrderItem, data)

            return {
                "success": True,
                "ItemId": new_item.ItemId
            }

        except Exception as e:
            logger.error(f"❌ Create item failed: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # Get Items by Order
    # ------------------------------------------------------------
    async def get_items_by_order(self, order_id: int):
        try:
            await self.db_manager.connect()
            items = await self.db_manager.read(
                RetailerOrderItem, {"OrderId": order_id}
            )

            return [
                RetailerOrderItemRead.from_orm(i).dict()
                for i in items
            ]

        except Exception as e:
            logger.error(f"❌ Fetch items failed: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # Update Item
    # ------------------------------------------------------------
    async def update_item(self, item_id: int, data: RetailerOrderItemUpdate):
        try:
            await self.db_manager.connect()
            count = await self.db_manager.update(
                RetailerOrderItem,
                {"ItemId": item_id},
                data.dict(exclude_unset=True)
            )

            if count:
                return {"success": True, "message": "Item updated"}

            return {"success": False, "message": "Item not found"}

        except Exception as e:
            logger.error(f"❌ Update item failed: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    # Delete Item
    # ------------------------------------------------------------
    async def delete_item(self, item_id: int):
        try:
            await self.db_manager.connect()
            count = await self.db_manager.delete(
                RetailerOrderItem, {"ItemId": item_id}
            )

            if count:
                return {"success": True, "message": "Item deleted"}

            return {"success": False, "message": "Item not found"}

        except Exception as e:
            logger.error(f"❌ Delete item failed: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()
