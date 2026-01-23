from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ...utils.timezone import ist_now


class RetailerInvoiceItemBase(BaseModel):
    OrderId: Optional[int]
    DistributorId: Optional[int]
    MedicineName: Optional[str]
    Brand: Optional[str]
    Quantity: Optional[int]
    Price: Optional[float]
    TotalAmount: Optional[float]

    class Config:
        from_attributes = True


class RetailerInvoiceItemCreate(RetailerInvoiceItemBase):
    MedicineName: str
    Quantity: int


class RetailerInvoiceItemRead(RetailerInvoiceItemBase):
    ItemId: int
    # CreatedAt: ist_now


class RetailerInvoiceBase(BaseModel):
    OrderId: Optional[int]
    DistributorId: Optional[int]
    RetailerName: Optional[str]
    InvoiceDate: Optional[datetime] = Field(default_factory=ist_now)
    DueDate: Optional[datetime] = Field(default_factory=ist_now)
    TotalAmount: Optional[float]
    TaxAmount: Optional[float]
    DiscountAmount: Optional[float]
    NetAmount: Optional[float]
    PaymentStatus: Optional[str]
    PaymentMode: Optional[str]
    PaymentTransactionId: Optional[str]
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]

    class Config:
        from_attributes = True


class RetailerInvoiceCreate(RetailerInvoiceBase):
    OrderId: int
    DistributorId: Optional[int]
    RetailerName: str
    Items: List[RetailerInvoiceItemCreate]


class RetailerInvoiceUpdate(RetailerInvoiceBase):
    pass


class RetailerInvoiceRead(RetailerInvoiceBase):
    InvoiceId: int
    # CreatedAt: datetime = Field(default_factory=ist_now)
    # UpdatedAt: datetime = Field(default_factory=ist_now)
    # Items: Optional[List[RetailerInvoiceItemRead]]
