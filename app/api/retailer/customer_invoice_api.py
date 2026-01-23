from fastapi import APIRouter, HTTPException
from typing import Optional
from ...schemas.retailer.customer_invoice_schema import CustomerInvoiceCreate, CustomerInvoiceUpdate
from ...crud.retailer.customer_invoice_manager import CustomerInvoiceManager
from ...config import settings


class CustomerInvoiceAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = CustomerInvoiceManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/retailer/invoices")(self.create_invoice)
        self.router.get("/retailer/invoices/{invoice_id}")(self.get_invoice)
        self.router.get("/retailer/{retailer_id}/invoices")(self.get_all_invoices)                # Filter by retailer
        self.router.put("/retailer/invoices/{invoice_id}")(self.update_invoice)
        self.router.delete("/retailer/invoices/{invoice_id}")(self.delete_invoice)
        self.router.delete("/retailer/{retailer_id}/invoices")(self.delete_all_invoices)


    # -----------------------------
    # Create Invoice
    # -----------------------------
    async def create_invoice(self, invoice: CustomerInvoiceCreate):
        try:
            return await self.crud.create_invoice(invoice)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Get Invoice by ID
    # -----------------------------
    async def get_invoice(self, invoice_id: int):
        try:
            return await self.crud.get_invoice(invoice_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Get All Invoices (by retailer)
    # -----------------------------
    async def get_all_invoices(self, retailer_id: Optional[int] = None):
        try:
            return await self.crud.get_all_invoices_by_retailer(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Update Invoice
    # -----------------------------
    async def update_invoice(self, invoice_id: int, data: CustomerInvoiceUpdate):
        try:
            return await self.crud.update_invoice(invoice_id, data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

        # -----------------------------
    # Delete Invoice by ID
    # -----------------------------
    async def delete_invoice(self, invoice_id: int):
        try:
            return await self.crud.delete_invoice(invoice_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Delete All Invoices (Optionally by Retailer)
    # -----------------------------
    async def delete_all_invoices(self, retailer_id: int):
        try:
            return await self.crud.delete_all_invoices(retailer_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
