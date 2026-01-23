from pydantic import BaseModel
from typing import List, Dict, Optional

class RetailerTopSellingProduct(BaseModel):
    MedicineName: str
    Quantity: int
    UnitPrice: float

class RetailerSalesDashboard(BaseModel):
    TotalRevenue: float
    TotalOrders: int
    AvgOrderValue: float
    SalesTrend: List[Dict[str, float]]  # [{“Jan”: 40000, …}]
    OrderVolume: List[Dict[str, int]]   # [{“Jan”: 100, …}]
    TopSellingProduct: List[RetailerTopSellingProduct]
