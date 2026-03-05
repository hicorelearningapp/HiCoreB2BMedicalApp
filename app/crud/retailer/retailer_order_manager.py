from typing import Optional, Dict, Any, List
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

# Invoice Imports for Auto-generation
from ...models.distributor.retailer_invoice_model import RetailerInvoice, RetailerInvoiceItem
from ...schemas.distributor.retailer_invoice_schema import (
    RetailerInvoiceCreate,
    RetailerInvoiceUpdate,
    RetailerInvoiceRead,
)

logger = get_logger(__name__)


class RetailerOrderManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)
        # Initialize Invoice Manager for internal calls
        self.invoice_manager = RetailerInvoiceManager(db_type)

    # ------------------------------------------------------------
    #  Create Order + Items
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

            logger.info(f" Retailer Order {order_id} created with items")

            return {
                "success": True,
                "message": "Retailer order created successfully",
                "OrderId": order_id,
            }

        except Exception as e:
            logger.error(f" Error creating retailer order: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    #  Get Order + Items (Filtered Retailer Fields)
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
            logger.error(f" Error fetching retailer order {order_id}: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()


    # ------------------------------------------------------------
    #  Get All Orders (filter by Retailer)
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
            logger.error(f" Error fetching orders: {e}")
            return {"success": False, "message": f"Error fetching orders: {e}"}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    #  Get All Orders (filter by Distributor)
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
            logger.error(f" Error fetching orders: {e}")
            return {"success": False, "message": f"Error fetching orders: {e}"}

        finally:
            await self.db_manager.disconnect()

    # ------------------------------------------------------------
    #  Update Order
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
            logger.error(f" Error updating retailer order: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    
    # ------------------------------------------------------------
    #  Update Order Status ONLY + Auto Invoice Generation
    # ------------------------------------------------------------
    async def update_order_status(self, order_id: int, status: str) -> dict:
        try:
            await self.db_manager.connect()
            print(f"DEBUG: Updating Order {order_id} status to {status}")

            rowcount = await self.db_manager.update(
                RetailerOrder,
                {"OrderId": order_id},
                {
                    "Status": status,
                    "UpdatedAt": ist_now()
                }
            )

            if rowcount:
                invoice_msg = ""
                if status == "Accepted":
                    print(f"DEBUG: Triggering Auto-Invoice for Order {order_id}")
                    invoice_gen = await self._handle_auto_invoice(order_id)
                    if invoice_gen.get("success"):
                        invoice_msg = f" and invoice #{invoice_gen.get('InvoiceId')} generated"
                    else:
                        invoice_gen_err = invoice_gen.get('message')
                        invoice_msg = f" but invoice generation failed: {invoice_gen_err}"
                        print(f"DEBUG: Auto-Invoice failed: {invoice_gen_err}")

                return {
                    "success": True,
                    "message": f"Order status updated to {status}{invoice_msg}"
                }

            return {"success": False, "message": "Order not found"}

        except Exception as e:
            logger.error(f" Error updating order status: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()

    async def _handle_auto_invoice(self, order_id: int) -> dict:
        """Internal helper to convert Order data to Invoice data and create it"""
        try:
            # 1. Fetch the complete order details
            order_details = await self.get_order(order_id)
            if not order_details or "OrderId" not in order_details:
                return {"success": False, "message": "Order details not found"}

            retailer_info = order_details.get("Retailer") or {}
            retailer_name = retailer_info.get("ShopName") or "Retailer"
            print(f"DEBUG: Mapping items for Order {order_id}")

            # 2. Prepare items for the invoice creation schema
            invoice_items_dicts = []
            total_sum = 0.0
            for item in order_details.get("Items", []):
                price = item.get("Price") or 0.0
                qty = item.get("Quantity") or 0
                item_total = price * qty
                total_sum += item_total
                
                # CRITICAL FIX: Creating a direct dictionary to ensure 'Brand' is present
                # before casting to the Pydantic model.
                item_obj = {
                    "OrderId": order_id,
                    "RetailerId": order_details.get("RetailerId"),
                    "DistributorId": order_details.get("DistributorId"),
                    "MedicineId": item.get("MedicineId") or item.get("ProductId"),
                    "MedicineName": item.get("MedicineName") or "Unknown Medicine",
                    "Brand": item.get("Brand") or "Generic",  # Mandatory field
                    "Quantity": qty,
                    "Price": price,
                    "TotalAmount": item_total
                }
                invoice_items_dicts.append(RetailerOrderItemCreate(**item_obj))

            # 3. Create the Invoice Create Schema
            invoice_data = RetailerInvoiceCreate(
                OrderId=order_id,
                RetailerId=order_details.get("RetailerId"),
                RetailerName=retailer_name,
                DistributorId=order_details.get("DistributorId"),
                Items=invoice_items_dicts,
                TotalAmount=total_sum,
                NetAmount=total_sum,
                TaxAmount=0.0,
                DiscountAmount=0.0,
                PaymentMode=order_details.get("PaymentMode") or "Pending",
                PaymentStatus="Pending",
                PaymentTransactionId="AUTO-GEN",
                CreatedBy="System",
                UpdatedBy="System",
                Notes=f"Auto-generated from Order ID: {order_id}"
            )
            print(f"DEBUG: Sending invoice data to Manager for Order {order_id}")

            # 4. Use existing Invoice Manager to save to DB
            return await self.invoice_manager.create_invoice(invoice_data)

        except Exception as e:
            print(f"DEBUG: Exception in _handle_auto_invoice: {str(e)}")
            return {"success": False, "message": str(e)}

    # ------------------------------------------------------------
    #  Delete Order + Items
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
            logger.error(f" Error deleting retailer order: {e}")
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
            logger.error(f" Create item failed: {e}")
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
            logger.error(f" Fetch items failed: {e}")
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
            logger.error(f" Update item failed: {e}")
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
            logger.error(f" Delete item failed: {e}")
            return {"success": False, "message": str(e)}

        finally:
            await self.db_manager.disconnect()


class RetailerInvoiceManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def create_invoice(self, invoice: RetailerInvoiceCreate) -> dict:
        await self.db_manager.connect()
        try:
            invoice_data = invoice.dict(exclude={"Items"})
            invoice_data["InvoiceDate"] = ist_now()

            total_amount = sum([(item.Price or 0) * (item.Quantity or 0) for item in invoice.Items])
            invoice_data["TotalAmount"] = total_amount
            invoice_data["NetAmount"] = total_amount + (invoice_data.get("TaxAmount") or 0) - (invoice_data.get("DiscountAmount") or 0)

            new_invoice = await self.db_manager.create(RetailerInvoice, invoice_data)
            invoice_id = new_invoice.InvoiceId

            for item in invoice.Items:
                item_data = item.dict()
                item_data["InvoiceId"] = invoice_id
                item_data["OrderId"] = invoice.OrderId
                item_data["DistributorId"] = invoice.DistributorId
                item_data["TotalAmount"] = (item.Price or 0) * (item.Quantity or 0)
                await self.db_manager.create(RetailerInvoiceItem, item_data)

            return {"success": True, "message": "Invoice created successfully", "InvoiceId": invoice_id}

        finally:
            await self.db_manager.disconnect()

    async def get_invoice(self, invoice_id: int) -> dict:
        await self.db_manager.connect()
        try:
            invoices = await self.db_manager.read(RetailerInvoice, {"InvoiceId": invoice_id})
            if not invoices:
                return {"success": False, "message": "Invoice not found"}

            invoice = invoices[0]
            items = await self.db_manager.read(RetailerInvoiceItem, {"InvoiceId": invoice_id})
            invoice_schema = RetailerInvoiceRead.from_orm(invoice).dict()
            invoice_schema["Items"] = [item.__dict__ for item in items]

            return invoice_schema
        finally:
            await self.db_manager.disconnect()

    async def update_invoice(self, invoice_id: int, data: RetailerInvoiceUpdate) -> dict:
        await self.db_manager.connect()
        try:
            rowcount = await self.db_manager.update(RetailerInvoice, {"InvoiceId": invoice_id}, data.dict(exclude_unset=True))
            if rowcount:
                return {"success": True, "message": "Invoice updated successfully"}
            return {"success": False, "message": "Invoice not found or no changes made"}
        finally:
            await self.db_manager.disconnect()

    async def get_all_invoices_by_distributor(self, distributor_id: Optional[int] = None) -> list:
        try:
            await self.db_manager.connect()
            query = {"DistributorId": distributor_id} if distributor_id else None
            invoices = await self.db_manager.read(RetailerInvoice, query)
            total_invoices = len(invoices)
            total_amount = sum([i.TotalAmount or 0 for i in invoices])
            completed = len([i for i in invoices if i.PaymentStatus == "Completed"])
            pending = len([i for i in invoices if i.PaymentStatus == "Pending"])
            cancelled = len([i for i in invoices if i.PaymentStatus == "Cancelled"])
            overdue = len([i for i in invoices if i.PaymentStatus == "Overdue"])
            invoice_data = [i.__dict__ for i in invoices]

            return {
                "TotalInvoices": total_invoices,
                "Completed": completed,
                "Pending": pending,
                "Cancelled": cancelled,
                "Overdue": overdue,
                "TotalAmount": total_amount,
                "Invoices": invoice_data
            }
            
        finally:
            await self.db_manager.disconnect()


    async def delete_invoice(self, invoice_id: int) -> dict:
        await self.db_manager.connect()
        try:
            # First remove invoice items
            await self.db_manager.delete(RetailerInvoiceItem, {"InvoiceId": invoice_id})
            
            # Then remove invoice
            rowcount = await self.db_manager.delete(RetailerInvoice, {"InvoiceId": invoice_id})

            if rowcount:
                return {"success": True, "message": "Invoice deleted successfully"}
            return {"success": False, "message": "Invoice not found"}

        finally:
            await self.db_manager.disconnect()

    async def delete_all_invoices(self, distributor_id: int) -> dict:
        await self.db_manager.connect()
        try:
            # First fetch all invoices for distributor
            invoices = await self.db_manager.read(RetailerInvoice, {"DistributorId": distributor_id})
            if not invoices:
                return {"success": False, "message": "No invoices found for this distributor"}

            invoice_ids = [inv.InvoiceId for inv in invoices]

            # Delete related invoice items
            for inv_id in invoice_ids:
                await self.db_manager.delete(RetailerInvoiceItem, {"InvoiceId": inv_id})

            # Delete invoices
            rowcount = await self.db_manager.delete(RetailerInvoice, {"DistributorId": distributor_id})

            return {
                "success": True,
                "message": f"Deleted {rowcount} invoices for distributor {distributor_id}",
                "DeletedCount": rowcount
            }
        finally:
            await self.db_manager.disconnect()