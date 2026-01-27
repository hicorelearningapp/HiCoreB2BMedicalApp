from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ...utils.timezone import ist_now


# =====================================================
# PHARMA ORDER ITEM SCHEMAS
# =====================================================
class PharmaOrderItemBase(BaseModel):
    PONumber: Optional[int]
    DistributorId: Optional[int]

    MedicineName: str
    Brand: Optional[str]
    Quantity: int
    Price: Optional[float]
    TotalAmount: Optional[float]
    Batch: Optional[str]
    ExpiryDate: Optional[datetime]


class PharmaOrderItemCreate(PharmaOrderItemBase):
    pass


class PharmaOrderItemUpdate(BaseModel):
    MedicineName: Optional[str]
    Brand: Optional[str]
    Quantity: Optional[int]
    Price: Optional[float]
    TotalAmount: Optional[float]
    Batch: Optional[str]
    ExpiryDate: Optional[datetime]


class PharmaOrderItemRead(PharmaOrderItemBase):
    ItemId: int
    CreatedAt: datetime

    class Config:
        from_attributes = True


# =====================================================
# PHARMA ORDER SCHEMAS
# =====================================================
class PharmaOrderBase(BaseModel):
    DistributorId: Optional[int]
    PharmaId: Optional[int]

    OrderDate: Optional[datetime] = Field(default_factory=ist_now)
    ExpectedDelivery: Optional[datetime]

    TotalItems: Optional[int]
    TotalAmount: Optional[float]

    Status: Optional[str] = "Placed"

    CreatedAt: Optional[datetime] = Field(default_factory=ist_now)
    UpdatedAt: Optional[datetime] = Field(default_factory=ist_now)
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]


class PharmaOrderCreate(PharmaOrderBase):
    DistributorId: int
    PharmaId: int


class PharmaOrderUpdate(BaseModel):
    ExpectedDelivery: Optional[datetime]
    Status: Optional[str]
    UpdatedBy: Optional[str]


class PharmaOrderRead(PharmaOrderBase):
    PONumber: int
    Items: Optional[List[PharmaOrderItemRead]] = []

    class Config:
        from_attributes = True
