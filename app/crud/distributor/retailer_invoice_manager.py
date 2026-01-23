from typing import List, Optional
from ...utils.timezone import ist_now
from ...db.base.database_manager import DatabaseManager
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



