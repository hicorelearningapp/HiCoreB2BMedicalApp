from pydantic import BaseModel
from typing import List, Dict, Optional

class DistributorTopSellingProduct(BaseModel):
    MedicineName: str
    Quantity: int
    UnitPrice: float

class DistributorSalesDashboard(BaseModel):
    TotalRevenue: float
    TotalOrders: int
    AvgOrderValue: float
    SalesTrend: List[Dict[str, float]]  # [{“Jan”: 40000, …}]
    OrderVolume: List[Dict[str, int]]   # [{“Jan”: 100, …}]
    TopSellingProduct: List[DistributorTopSellingProduct]
