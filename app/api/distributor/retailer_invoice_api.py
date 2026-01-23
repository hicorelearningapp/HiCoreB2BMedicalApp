from fastapi import APIRouter, HTTPException
from typing import Optional
from ...schemas.distributor.retailer_invoice_schema import RetailerInvoiceCreate, RetailerInvoiceUpdate
from ...crud.distributor.retailer_invoice_manager import RetailerInvoiceManager
from ...config import settings


class RetailerInvoiceAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = RetailerInvoiceManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/distributor/invoices")(self.create_invoice)
        self.router.get("/distributor/invoices/{invoice_id}")(self.get_invoice)
        self.router.get("/distributor/{distributor_id}/invoices")(self.get_all_invoices)                # Filter by distributor
        self.router.put("/distributor/invoices/{invoice_id}")(self.update_invoice)
        self.router.delete("/distributor/invoices/{invoice_id}")(self.delete_invoice)
        self.router.delete("/distributor/{distributor_id}/invoices")(self.delete_all_invoices)


    # -----------------------------
    # Create Invoice
    # -----------------------------
    async def create_invoice(self, invoice: RetailerInvoiceCreate):
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
    # Get All Invoices (by distributor)
    # -----------------------------
    async def get_all_invoices(self, distributor_id: Optional[int] = None):
        try:
            return await self.crud.get_all_invoices_by_distributor(distributor_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # Update Invoice
    # -----------------------------
    async def update_invoice(self, invoice_id: int, data: RetailerInvoiceUpdate):
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
    # Delete All Invoices (Optionally by Distributor)
    # -----------------------------
    async def delete_all_invoices(self, distributor_id: int):
        try:
            return await self.crud.delete_all_invoices(distributor_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
