from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ...utils.timezone import ist_now


# ----------------- OrderItem Schemas -----------------
class RetailerOrderItemBase(BaseModel):
    OrderId: Optional[int]
    RetailerId: Optional[int]    
    DistributorId: Optional[int]    
    MedicineId: int
    MedicineName: str
    Quantity: int
    Price: float   
    TotalAmount: float  


class RetailerOrderItemCreate(RetailerOrderItemBase):
    pass


class RetailerOrderItemUpdate(RetailerOrderItemBase):
    pass


class RetailerOrderItemRead(RetailerOrderItemBase):
    ItemId: int

    class Config:
        from_attributes = True


# ----------------- Order Schemas -----------------
class RetailerOrderBase(BaseModel):
    RetailerId: Optional[int]
    DistributorId: Optional[int]
    DistributorName: Optional[str]
    
    OrderDateTime: Optional[datetime] = Field(default_factory=ist_now)
    ExpectedDelivery: Optional[datetime] = Field(default_factory=ist_now)

    DeliveryMode: Optional[str]
    DeliveryService: Optional[str]
    DeliveryPartnerTrackingId: Optional[str]
    DeliveryStatus: Optional[str] = "Pending"

    PaymentMode: Optional[str]
    PaymentStatus: Optional[str] = "Pending"
    PaymentTransactionId: Optional[str]
    
    TotalItems: Optional[int]
    TotalAmount: Optional[float] = 0.0  

    Status: Optional[str] = "New"

    CreatedAt: Optional[datetime] = Field(default_factory=ist_now)
    UpdatedAt: Optional[datetime] = Field(default_factory=ist_now)


class RetailerOrderCreate(RetailerOrderBase):
    Items: Optional[List[RetailerOrderItemCreate]]


class RetailerOrderUpdate(RetailerOrderBase):
    pass


class RetailerOrderRead(RetailerOrderBase):
    OrderId: int
    # Items: Optional[List[RetailerOrderItemRead]]

    class Config:
        from_attributes = True
