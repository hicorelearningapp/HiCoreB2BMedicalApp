from ...utils.timezone import ist_now
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_order_model import RetailerOrder, RetailerOrderItem
from ...models.retailer.retailer_model import Retailer
from ...models.distributor.distributor_model import Distributor
from ...schemas.retailer.retailer_order_schema import (
    RetailerOrderCreate,
    RetailerOrderItemCreate,
    RetailerOrderItemUpdate
)
from ...utils.logger import get_logger

logger = get_logger(__name__)


class RetailerOrderManager:
    def __init__(self, db_type: str):
        self.db = DatabaseManager(db_type)

    # ------------------------
    # Create Retailer Order
    # ------------------------
    async def create_order(self, order_data: RetailerOrderCreate, items: list):
        try:
            await self.db.connect()

            total_amount = 0
            for i in items:
                base_amount = i.UnitPrice * i.Quantity
                gst_amount = (base_amount * i.GSTPercentage) / 100
                total_amount += (base_amount + gst_amount)

            order_dict = order_data.dict()
            order_dict["Amount"] = total_amount
            order_dict["CreatedAt"] = ist_now()
            order_dict["UpdatedAt"] = ist_now()

            order_obj = await self.db.create(RetailerOrder, order_dict)
            order_id = order_obj.OrderId

            # Insert order items
            for i in items:
                item_dict = i.dict()
                item_dict["OrderId"] = order_id

                base_amount = i.UnitPrice * i.Quantity
                gst_amount = (base_amount * i.GSTPercentage) / 100
                item_dict["TotalAmount"] = base_amount + gst_amount

                await self.db.create(RetailerOrderItem, item_dict)

            return {"success": True, "OrderId": order_id}

        except Exception as e:
            logger.error(f"Create Retailer Order error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Get Retailer Order by OrderId
    # ------------------------
    async def get_order(self, order_id: int):
        try:
            await self.db.connect()

            order_list = await self.db.read(RetailerOrder, {"OrderId": order_id})
            if not order_list:
                return {"success": False, "message": "Order not found"}

            order = order_list[0]

            # Fetch order items
            items = await self.db.read(RetailerOrderItem, {"OrderId": order.OrderId})
            item_data = [
                {
                    "MedicineId": i.MedicineId,
                    "MedicineName": i.MedicineName,
                    "Quantity": i.Quantity,
                    "UnitPrice": i.UnitPrice,
                    "GSTPercentage": i.GSTPercentage,
                    "TotalAmount": i.TotalAmount
                }
                for i in items
            ]

            # Fetch retailer info (with address from the same table)
            retailer_list = await self.db.read(Retailer, {"RetailerId": order.RetailerId})
            retailer = retailer_list[0] if retailer_list else None

            retailer_info = {
                "RetailerId": retailer.RetailerId if retailer else None,
                "ShopName": retailer.ShopName if retailer else "",
                "OwnerName": retailer.OwnerName if retailer else "",
                "PhoneNumber": retailer.PhoneNumber if retailer else "",
                "Email": retailer.Email if retailer else "",
                "AddressLine1": retailer.AddressLine1 if retailer else "",
                "AddressLine2": retailer.AddressLine2 if retailer else "",
                "City": retailer.City if retailer else "",
                "State": retailer.State if retailer else "",
                "Country": retailer.Country if retailer else "",
                "PostalCode": retailer.PostalCode if retailer else "",
                "Latitude": retailer.Latitude if retailer else None,
                "Longitude": retailer.Longitude if retailer else None
            }

            print(order.DistributorId)
            # Fetch Distributor Info
            distributor_list = await self.db.read(Distributor, {"DistributorId": order.DistributorId})
            # print(distributor_list)
            distributor = distributor_list[0] if distributor_list else None

            distributor_info = {
                "DistributorId": distributor.DistributorId if distributor else None,
                "Name": distributor.ContactPersonName if distributor else "",
                "PhoneNumber": distributor.PhoneNumber if distributor else "",
                "Email": distributor.Email if distributor else "",
                "AddressLine1": distributor.AddressLine1 if distributor else "",
                "AddressLine2": distributor.AddressLine2 if distributor else "",
                "City": distributor.City if distributor else "",
                "State": distributor.State if distributor else "",
                "Country": distributor.Country if distributor else "",
                "PostalCode": distributor.PostalCode if distributor else "",
                "Latitude": distributor.Latitude if distributor else None,
                "Longitude": distributor.Longitude if distributor else None
            }

            return {
                "success": True,
                "OrderId": order.OrderId,
                "Amount": order.Amount,
                "OrderDate": order.OrderDateTime,
                "OrderStage": order.OrderStage,
                "OrderStatus": order.OrderStatus,
                "DeliveryMode": order.DeliveryMode,
                "DeliveryService": order.DeliveryService,
                "DeliveryPartnerTrackingId": order.DeliveryPartnerTrackingId,
                "PaymentMode": order.PaymentMode,
                "PaymentStatus": order.PaymentStatus,
                "InvoiceId": order.InvoiceId,
                "Retailer": retailer_info,
                "Distributor": distributor_info,
                "Items": item_data
            }

        except Exception as e:
            logger.error(f"Get Retailer Order error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Update Order
    # ------------------------
    async def update_order(self, order_id: int, data: dict):
        try:
            await self.db.connect()
            data["UpdatedAt"] = ist_now()
            updated = await self.db.update(RetailerOrder, {"OrderId": order_id}, data)

            if updated:
                return {"success": True, "message": "Order updated"}

            return {"success": False, "message": "Order not found"}

        except Exception as e:
            logger.error(f"Update Retailer Order error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Delete Order
    # ------------------------
    async def delete_order(self, order_id: int):
        try:
            await self.db.connect()

            await self.db.delete(RetailerOrderItem, {"OrderId": order_id})
            deleted = await self.db.delete(RetailerOrder, {"OrderId": order_id})

            if deleted:
                return {"success": True, "message": "Order deleted"}

            return {"success": False, "message": "Order not found"}

        except Exception as e:
            logger.error(f"Delete Retailer Order error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Get Orders by Retailer
    # ------------------------
    async def get_orders_by_retailer(self, retailer_id: int):
        try:
            await self.db.connect()

            orders = await self.db.read(RetailerOrder, {"RetailerId": retailer_id})
            if not orders:
                return {"TotalOrders": 0, "Delivered": 0, "Processing": 0, "Pending": 0, "Orders": []}

            result = {"TotalOrders": len(orders), "Delivered": 0, "Pending": 0, "Processing": 0, "Orders": []}

            for o in orders:
                if o.OrderStatus == "Delivered":
                    result["Delivered"] += 1
                elif o.OrderStatus == "Processing":
                    result["Processing"] += 1
                else:
                    result["Pending"] += 1

                distributor_list = await self.db.read(Distributor, {"DistributorId": o.DistributorId})
                distributor = distributor_list[0] if distributor_list else None

                items = await self.db.read(RetailerOrderItem, {"OrderId": o.OrderId})
                items_count = len(items)

                result["Orders"].append({
                    "OrderId": o.OrderId,
                    "DistributorName": o.DistributorName,  # distributor.ContactPersonName if distributor else "",
                    "ItemsCount": items_count,
                    "Amount": o.Amount,
                    "OrderDate": o.OrderDateTime,
                    "ExpectedDelivery": o.ExpectedDelivery,
                    "Status": o.OrderStatus
                })

            return result

        except Exception as e:
            logger.error(f"Get orders by retailer error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Get Orders by Distributor
    # ------------------------
    async def get_orders_by_distributor(self, distributor_id: int):
        try:
            await self.db.connect()

            orders = await self.db.read(RetailerOrder, {"DistributorId": distributor_id})
            if not orders:
                return {"TotalOrders": 0, "Delivered": 0, "Processing": 0, "Pending": 0, "NewOrders": []}

            result = {"TotalOrders": len(orders), "Delivered": 0, "Processing": 0, "Pending": 0, "NewOrders": []}

            for o in orders:
                if o.OrderStatus == "Delivered":
                    result["Delivered"] += 1
                elif o.OrderStatus == "Processing":
                    result["Processing"] += 1
                else:
                    result["Pending"] += 1

                retailer_list = await self.db.read(Retailer, {"RetailerId": o.RetailerId})
                retailer = retailer_list[0] if retailer_list else None

                items = await self.db.read(RetailerOrderItem, {"OrderId": o.OrderId})
                med_list = [{"MedicineName": i.MedicineName, "Quantity": i.Quantity} for i in items]

                result["NewOrders"].append({
                    "OrderId": o.OrderId,
                    "RetailerName": retailer.ShopName if retailer else "",
                    "RetailerPhone": retailer.PhoneNumber if retailer else "",
                    "RetailerEmail": retailer.Email if retailer else "",
                    "GSTNumber": retailer.GSTNumber if retailer else "",
                    "LicenseNumber": retailer.LicenseNumber if retailer else "",
                    "OrderDate": o.OrderDateTime,
                    "MedicineRequested": med_list
                })

            return result

        except Exception as e:
            logger.error(f"Get orders by distributor error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()


class RetailerOrderItemManager:
    def __init__(self, db_type: str):
        self.db = DatabaseManager(db_type)

    # ------------------------
    # Create a single order item
    # ------------------------
    async def create_item(self, item_data: dict):
        try:
            await self.db.connect()
            item_data["CreatedAt"] = ist_now()
            item_obj = await self.db.create(RetailerOrderItem, item_data)
            return {"success": True, "ItemId": item_obj.ItemId}
        except Exception as e:
            logger.error(f"Create Retailer Order Item error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Get items by OrderId
    # ------------------------
    async def get_items_by_order(self, order_id: int):
        try:
            await self.db.connect()
            items = await self.db.read(RetailerOrderItem, {"OrderId": order_id})
            item_list = [
                {
                    "ItemId": i.ItemId,
                    "OrderId": i.OrderId,
                    "RetailerId": i.RetailerId,
                    "DistributorId": i.DistributorId,
                    "MedicineId": i.MedicineId,
                    "MedicineName": i.MedicineName,
                    "Quantity": i.Quantity,
                    "UnitPrice": i.UnitPrice,
                    "GSTPercentage": i.GSTPercentage,
                    "TotalAmount": i.TotalAmount
                }
                for i in items
            ]
            return {"success": True, "Items": item_list}
        except Exception as e:
            logger.error(f"Get Retailer Order Items error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Update an order item
    # ------------------------
    async def update_item(self, item_id: int, data: dict):
        try:
            await self.db.connect()
            data["UpdatedAt"] = ist_now()
            updated = await self.db.update(RetailerOrderItem, {"ItemId": item_id}, data)
            if updated:
                return {"success": True, "message": "Item updated"}
            return {"success": False, "message": "Item not found"}
        except Exception as e:
            logger.error(f"Update Retailer Order Item error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()

    # ------------------------
    # Delete an order item
    # ------------------------
    async def delete_item(self, item_id: int):
        try:
            await self.db.connect()
            deleted = await self.db.delete(RetailerOrderItem, {"ItemId": item_id})
            if deleted:
                return {"success": True, "message": "Item deleted"}
            return {"success": False, "message": "Item not found"}
        except Exception as e:
            logger.error(f"Delete Retailer Order Item error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db.disconnect()