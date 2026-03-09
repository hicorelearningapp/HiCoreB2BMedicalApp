from typing import List, Optional
from ...utils.timezone import ist_now
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_model import Retailer
from ...models.distributor.distributor_model import Distributor
from ...models.retailer.retailer_order_model import RetailerOrder
from ...models.distributor.retailer_invoice_model import RetailerInvoice, RetailerInvoiceItem
from ...schemas.distributor.retailer_invoice_schema import (
    RetailerInvoiceCreate,
    RetailerInvoiceUpdate,
    RetailerInvoiceRead,
)   


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

            # Fetch order
            orders = await self.db_manager.read(RetailerOrder, {"OrderId": invoice.OrderId})
            order = orders[0] if orders else None

            # Fetch retailer
            retailers = await self.db_manager.read(Retailer, {"RetailerId": order.RetailerId}) if order else []
            retailer = retailers[0] if retailers else None

            # Fetch distributor
            distributors = await self.db_manager.read(Distributor, {"DistributorId": invoice.DistributorId})
            distributor = distributors[0] if distributors else None

            # Fetch invoice items
            items = await self.db_manager.read(RetailerInvoiceItem, {"InvoiceId": invoice_id})

            item_list = []
            total_amount = 0

            for item in items:
                gst_rate = 5
                gst_amount = ((item.Price or 0) * gst_rate) / 100
                total = (item.Price or 0) * (item.Quantity or 0) + gst_amount

                total_amount += total

                item_list.append({
                    "ItemId": item.ItemId,
                    "Medicine": item.MedicineName,
                    "Quantity": item.Quantity,
                    "UnitPrice": item.Price,
                    "GST": "5%",
                    "GSTAmount": round(gst_amount, 2),
                    "Total": round(total, 2)
                })

            response = {
                "InvoiceNo": f"INV-{invoice.InvoiceDate.year}-{invoice.InvoiceId}",

                "RetailerDetails": {
                    "Name": retailer.OwnerName if retailer else None,
                    "Address": f"{retailer.AddressLine1}, {retailer.City}, {retailer.State} - {retailer.PostalCode}" if retailer else None,
                    "Contact": retailer.PhoneNumber if retailer else None,
                    "Email": retailer.Email if retailer else None,
                    "OrderID": f"ORD-{invoice.OrderId}",
                    "OrderDate": order.OrderDateTime.strftime("%d/%m/%Y") if order else None,
                    "ExpectedDelivery": order.ExpectedDelivery.strftime("%d/%m/%Y") if order and order.ExpectedDelivery else None
                },

                "OrderSummary": {
                    "Items": item_list,
                    "TotalAmount": round(total_amount, 2)
                },

                "PaymentAndDelivery": {
                    "PaymentMode": invoice.PaymentMode,
                    "PaymentStatus": invoice.PaymentStatus,
                    "DeliveryMethod": order.DeliveryMode if order else None,
                    "DeliveryPartner": order.DeliveryService if order else None
                },

                "DistributorDetails": {
                    "DistributorName": distributor.CompanyName if distributor else None,
                    "Address": f"{distributor.AddressLine1}, {distributor.City}, {distributor.State}" if distributor else None,
                    "LicenseNo": distributor.LicenseNumber if distributor else None,
                    "GSTIN": distributor.GSTNumber if distributor else None,
                    "Support": {
                        "Phone": distributor.PhoneNumber if distributor else None,
                        "Email": distributor.Email if distributor else None
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



