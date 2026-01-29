from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ...utils.timezone import ist_now


# =====================================================
# PHARMA ORDER ITEM SCHEMAS
# =====================================================
class PharmaOrderItemBase(BaseModel):
    PONumber: int
    DistributorId: int
    PharmaId: int

    MedicineId: int
    MedicineName: str
    Quantity: int
    Price: float
    TotalAmount: float
    

class PharmaOrderItemCreate(PharmaOrderItemBase):
    pass


class PharmaOrderItemUpdate(BaseModel):
    pass
    

class PharmaOrderItemRead(PharmaOrderItemBase):
    ItemId: int
    
    class Config:
        from_attributes = True


# =====================================================
# PHARMA ORDER SCHEMAS
# =====================================================
class PharmaOrderBase(BaseModel):
    DistributorId: Optional[int]
    PharmaId: Optional[int]
    PharmaName: Optional[str]

    OrderDate: Optional[datetime] = Field(default_factory=ist_now)
    ExpectedDelivery: Optional[datetime]

    TotalItems: Optional[int]
    TotalAmount: Optional[float]

    Status: Optional[str] = "New"

    CreatedAt: Optional[datetime] = Field(default_factory=ist_now)
    UpdatedAt: Optional[datetime] = Field(default_factory=ist_now)
    


class PharmaOrderCreate(PharmaOrderBase):
    Items: List[PharmaOrderItemCreate]


class PharmaOrderUpdate(BaseModel):
    ExpectedDelivery: Optional[datetime]
    Status: Optional[str]
    

class PharmaOrderRead(PharmaOrderBase):
    PONumber: int
    # Items: Optional[List[PharmaOrderItemRead]] = []

    class Config:
        from_attributes = True
