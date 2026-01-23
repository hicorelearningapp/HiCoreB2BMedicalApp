from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from ...utils.timezone import ist_now


class CustomerInvoiceItemBase(BaseModel):
    OrderId: Optional[int]
    RetailerId: Optional[int]
    MedicineName: Optional[str]
    Brand: Optional[str]
    Quantity: Optional[int]
    Price: Optional[float]
    TotalAmount: Optional[float]

    class Config:
        from_attributes = True


class CustomerInvoiceItemCreate(CustomerInvoiceItemBase):
    MedicineName: str
    Quantity: int


class CustomerInvoiceItemRead(CustomerInvoiceItemBase):
    ItemId: int
    CreatedAt: datetime = Field(default_factory=ist_now)


class CustomerInvoiceBase(BaseModel):
    OrderId: Optional[int]
    RetailerId: Optional[int]
    CustomerName: Optional[str]
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


class CustomerInvoiceCreate(CustomerInvoiceBase):
    OrderId: int
    RetailerId: Optional[int]
    CustomerName: str
    Items: List[CustomerInvoiceItemCreate]


class CustomerInvoiceUpdate(CustomerInvoiceBase):
    pass


class CustomerInvoiceRead(CustomerInvoiceBase):
    InvoiceId: int
    # CreatedAt: datetime = Field(default_factory=ist_now)
    # UpdatedAt: datetime = Field(default_factory=ist_now)
    # Items: Optional[List[CustomerInvoiceItemRead]]
