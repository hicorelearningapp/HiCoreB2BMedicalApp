from typing import List, Optional
import httpx
from ...utils.timezone import ist_now
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_model import Retailer
from ...models.retailer.customer_invoice_model import CustomerInvoice, CustomerInvoiceItem
from ...schemas.retailer.customer_invoice_schema import (
    CustomerInvoiceCreate,
    CustomerInvoiceUpdate,
    CustomerInvoiceRead,
)


# Local
GET_ORDER_BASE_URL = "http://127.0.0.1:8000/orders/"
GET_CUSTOMER_BASE_URL = "http://127.0.0.1:8000/customers/"

class CustomerInvoiceManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def create_invoice(self, invoice: CustomerInvoiceCreate) -> dict:
        await self.db_manager.connect()
        try:
            invoice_data = invoice.dict(exclude={"Items"})
            invoice_data["InvoiceDate"] = ist_now()

            total_amount = sum([(item.Price or 0) * (item.Quantity or 0) for item in invoice.Items])
            invoice_data["TotalAmount"] = total_amount
            invoice_data["NetAmount"] = total_amount + (invoice_data.get("TaxAmount") or 0) - (invoice_data.get("DiscountAmount") or 0)

            new_invoice = await self.db_manager.create(CustomerInvoice, invoice_data)
            invoice_id = new_invoice.InvoiceId

            for item in invoice.Items:
                item_data = item.dict()
                item_data["InvoiceId"] = invoice_id
                item_data["OrderId"] = invoice.OrderId
                item_data["RetailerId"] = invoice.RetailerId
                item_data["TotalAmount"] = (item.Price or 0) * (item.Quantity or 0)
                await self.db_manager.create(CustomerInvoiceItem, item_data)

            return {"success": True, "message": "Invoice created successfully", "InvoiceId": invoice_id}

        finally:
            await self.db_manager.disconnect()


    async def get_invoice(self, invoice_id: int) -> dict:
        await self.db_manager.connect()
        try:
            # -----------------------------
            # Fetch Invoice
            # -----------------------------
            invoices = await self.db_manager.read(CustomerInvoice, {"InvoiceId": invoice_id})
            if not invoices:
                return {"success": False, "message": "Invoice not found"}

            invoice = invoices[0]

            order = None
            customer = None

            async with httpx.AsyncClient() as client:

                # -----------------------------
                # Fetch Order from API
                # -----------------------------
                order_url = f"{GET_ORDER_BASE_URL}{invoice.OrderId}"
                order_resp = await client.get(order_url)

                if order_resp.status_code == 200:
                    order = order_resp.json()
                    customer = order.get("Customer")

            # -----------------------------
            # Fetch Retailer from DB
            # -----------------------------
            retailers = await self.db_manager.read(Retailer, {"RetailerId": invoice.RetailerId})
            retailer = retailers[0] if retailers else None

            # -----------------------------
            # Build Item List (from Order API)
            # -----------------------------
            item_list = []
            total_amount = 0

            if order and order.get("Items"):
                for item in order["Items"]:
                    gst_rate = 5

                    base_amount = (item.get("Price", 0)) * (item.get("Quantity", 0))
                    gst_amount = (base_amount * gst_rate) / 100
                    total = base_amount + gst_amount

                    total_amount += total

                    item_list.append({
                        "ItemId": item.get("OrderItemId"),
                        "Medicine": item.get("MedicineName"),
                        "Quantity": item.get("Quantity"),
                        "UnitPrice": item.get("Price"),
                        "GST": "5%",
                        "GSTAmount": round(gst_amount, 2),
                        "Total": round(total, 2)
                    })

            # -----------------------------
            # Build Invoice Response
            # -----------------------------
            response = {
                "InvoiceNo": f"INV-{invoice.InvoiceDate.year}-{invoice.InvoiceId}",

                "CustomerDetails": {
                    "Name": order.get("CustomerName") if order else None,
                    "Address": f"{customer.get('AddressLine1')}, {customer.get('City')}, {customer.get('State')} - {customer.get('PostalCode')}" if customer else None,
                    "Contact": customer.get("PhoneNumber") if customer else None,
                    "Email": customer.get("Email") if customer else None,
                    "OrderID": f"ORD-{invoice.OrderId}",
                    "OrderDate": order.get("OrderDateTime") if order else None,
                    "ExpectedDelivery": order.get("ExpectedDelivery") if order else None
                },

                "OrderSummary": {
                    "Items": item_list,
                    "TotalAmount": round(total_amount, 2)
                },

                "PaymentAndDelivery": {
                    "PaymentMode": invoice.PaymentMode,
                    "PaymentStatus": invoice.PaymentStatus,
                    "DeliveryMethod": order.get("DeliveryMode") if order else None,
                    "DeliveryPartner": order.get("DeliveryService") if order else None
                },

                "RetailerDetails": {
                    "ShopName": retailer.ShopName if retailer else None,
                    "RetailerName": retailer.OwnerName if retailer else None,
                    "Address": f"{retailer.AddressLine1}, {retailer.City}, {retailer.State}" if retailer else None,
                    "LicenseNo": retailer.LicenseNumber if retailer else None,
                    "GSTIN": retailer.GSTNumber if retailer else None,
                    "Support": {
                        "Phone": retailer.PhoneNumber if retailer else None,
                        "Email": retailer.Email if retailer else None
                    }
                },

                "FooterNotes": [
                    "All medicines are sold under valid license and verified prescriptions.",
                    "Prices include applicable taxes (GST @5%).",
                    "For replacement or issues, contact support within 24 hours of delivery."
                ]
            }

            return response

        finally:
            await self.db_manager.disconnect()

    async def update_invoice(self, invoice_id: int, data: CustomerInvoiceUpdate) -> dict:
        await self.db_manager.connect()
        try:
            rowcount = await self.db_manager.update(CustomerInvoice, {"InvoiceId": invoice_id}, data.dict(exclude_unset=True))
            if rowcount:
                return {"success": True, "message": "Invoice updated successfully"}
            return {"success": False, "message": "Invoice not found or no changes made"}
        finally:
            await self.db_manager.disconnect()

    async def get_all_invoices_by_retailer(self, retailer_id: Optional[int] = None) -> list:
        try:
            await self.db_manager.connect()
            query = {"RetailerId": retailer_id} if retailer_id else None
            invoices = await self.db_manager.read(CustomerInvoice, query)
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
            await self.db_manager.delete(CustomerInvoiceItem, {"InvoiceId": invoice_id})
            
            # Then remove invoice
            rowcount = await self.db_manager.delete(CustomerInvoice, {"InvoiceId": invoice_id})

            if rowcount:
                return {"success": True, "message": "Invoice deleted successfully"}
            return {"success": False, "message": "Invoice not found"}

        finally:
            await self.db_manager.disconnect()

    async def delete_all_invoices(self, retailer_id: int) -> dict:
        await self.db_manager.connect()
        try:
            # First fetch all invoices for retailer
            invoices = await self.db_manager.read(CustomerInvoice, {"RetailerId": retailer_id})
            if not invoices:
                return {"success": False, "message": "No invoices found for this retailer"}

            invoice_ids = [inv.InvoiceId for inv in invoices]

            # Delete related invoice items
            for inv_id in invoice_ids:
                await self.db_manager.delete(CustomerInvoiceItem, {"InvoiceId": inv_id})

            # Delete invoices
            rowcount = await self.db_manager.delete(CustomerInvoice, {"RetailerId": retailer_id})

            return {
                "success": True,
                "message": f"Deleted {rowcount} invoices for retailer {retailer_id}",
                "DeletedCount": rowcount
            }
        finally:
            await self.db_manager.disconnect()



