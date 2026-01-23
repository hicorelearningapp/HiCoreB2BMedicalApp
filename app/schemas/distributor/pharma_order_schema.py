from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ...utils.timezone import ist_now


# -------------------------------
# Pharma Order Item Schema
# -------------------------------
class PharmaOrderItemBase(BaseModel):
    PONumber: Optional[int]
    DistributorId: Optional[int]
    InventoryId: Optional[int]
    MedicineName: Optional[str]
    Brand: Optional[str]
    Quantity: Optional[int]
    Price: Optional[float]
    TotalAmount: Optional[float]
    Batch: Optional[str]
    ExpiryDate: Optional[datetime] = Field(default_factory=ist_now)

    class Config:
        from_attributes = True


class PharmaOrderItemCreate(PharmaOrderItemBase):
    MedicineName: str
    Quantity: int


class PharmaOrderItemRead(PharmaOrderItemBase):
    ItemId: int
    CreatedAt: datetime = Field(default_factory=ist_now)


# -------------------------------
# Pharma Order Schema
# -------------------------------
class PharmaOrderBase(BaseModel):
    DistributorId: Optional[int]
    PharmaName: Optional[str]
    OrderDate: Optional[datetime] = Field(default_factory=ist_now)
    ExpectedDelivery: Optional[datetime] = Field(default_factory=ist_now)
    TotalItems: Optional[int]
    TotalAmount: Optional[float]
    Status: Optional[str]
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]

    class Config:
        from_attributes = True


class PharmaOrderCreate(PharmaOrderBase):
    DistributorId: int
    PharmaName: str
    Items: List[PharmaOrderItemCreate]


class PharmaOrderUpdate(PharmaOrderBase):
    pass


class PharmaOrderRead(PharmaOrderBase):
    PONumber: int
    CreatedAt: datetime = Field(default_factory=ist_now)
    UpdatedAt: datetime = Field(default_factory=ist_now)
    Items: Optional[List[PharmaOrderItemRead]]
