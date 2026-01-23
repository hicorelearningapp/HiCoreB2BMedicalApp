from sqlalchemy import Column, Integer, String, Float, Date
from .sql_base import Base

class RetailerInventory(Base):
    __tablename__ = "RetailerInventory"

    RetailerInventoryId = Column(Integer, primary_key=True, index=True)
    RetailerId = Column(Integer, nullable=False)  # No foreign key
    MedicineName = Column(String, nullable=False)
    Brand = Column(String, nullable=True)
    MinStock = Column(Integer, nullable=True)
    MaxStock = Column(Integer, nullable=True)
    Price = Column(Float, nullable=False)
    Batch = Column(String, nullable=True)
    ExpiryDate = Column(Date, nullable=True)
    Status = Column(String, nullable=True)  # in, low, no
    Quantity = Column(Integer, nullable=False)
