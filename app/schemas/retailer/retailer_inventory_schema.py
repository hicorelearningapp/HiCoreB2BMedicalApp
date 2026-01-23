from pydantic import BaseModel
from typing import Optional
from datetime import date

class RetailerInventoryBase(BaseModel):
    RetailerId: Optional[int]
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

class RetailerInventoryCreate(RetailerInventoryBase):
    RetailerId: int
    MedicineName: str
    Price: float
    Quantity: int

class RetailerInventoryUpdate(RetailerInventoryBase):
    pass

class RetailerInventoryRead(RetailerInventoryBase):
    RetailerInventoryId: int

class RetailerInventorySummary(BaseModel):
    TotalItems: int
    InStock: int
    LowStock: int
    NoStock: int
