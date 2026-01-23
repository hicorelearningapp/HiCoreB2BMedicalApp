from pydantic import BaseModel
from typing import Optional
from datetime import date

class DistributorInventoryBase(BaseModel):
    DistributorId: Optional[int]
    MedicineName: Optional[str]
    Brand: Optional[str]
    MinStock: Optional[int]
    MaxStock: Optional[int]
    Price: Optional[float]
    Batch: Optional[str]
    ExpiryDate: Optional[date]
    Status: Optional[str]
    Quantity: Optional[int]

    class Config:
        from_attributes = True

class DistributorInventoryCreate(DistributorInventoryBase):
    DistributorId: int
    MedicineName: str
    Price: float
    Quantity: int

class DistributorInventoryUpdate(DistributorInventoryBase):
    pass

class DistributorInventoryRead(DistributorInventoryBase):
    DistributorInventoryId: int

class DistributorInventorySummary(BaseModel):
    TotalItems: int
    InStock: int
    LowStock: int
    NoStock: int
