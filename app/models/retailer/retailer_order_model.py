from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from ...utils.timezone import ist_now
from .sql_base import Base


class RetailerOrder(Base):
    __tablename__ = "RetailerOrders"

    OrderId = Column(Integer, primary_key=True, index=True)
    RetailerId = Column(Integer, nullable=False)
    DistributorId = Column(Integer, nullable=False)
    DistributorName = Column(String, nullable=False)
    
    OrderDateTime = Column(DateTime, default=ist_now)
    ExpectedDelivery = Column(DateTime, nullable=True)

    # Delivery info
    DeliveryMode = Column(String, nullable=True)
    DeliveryService = Column(String, nullable=True)
    DeliveryPartnerTrackingId = Column(String, nullable=True)
    DeliveryStatus = Column(String, default="Pending")  # Pending, Shipped, Delivered

    # Payment info
    PaymentMode = Column(String, nullable=True)
    PaymentStatus = Column(String, default="Pending")  # Pending, Paid, Failed
    PaymentTransactionId = Column(String, nullable=True)
    
    TotalItems = Column(Integer, nullable=True)
    TotalAmount = Column(Float, nullable=True)
    

    # Order state
    Status = Column(String, default="New")  

    # Audit fields
    CreatedAt = Column(DateTime, default=ist_now)
    UpdatedAt = Column(DateTime, default=ist_now, onupdate=ist_now)


class RetailerOrderItem(Base):
    __tablename__ = "RetailerOrderItem"

    ItemId = Column(Integer, primary_key=True, index=True)
    OrderId = Column(Integer, nullable=False)
    RetailerId = Column(Integer, nullable=False)
    DistributorId = Column(Integer, nullable=False)

    MedicineId = Column(Integer, nullable=False)
    MedicineName = Column(String, nullable=False)
    Quantity = Column(Integer, nullable=False)
    Price = Column(Float, nullable=True)
    TotalAmount = Column(Float, nullable=False)
