from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from ...utils.timezone import ist_now
from .sql_base import Base


class RetailerOrder(Base):
    __tablename__ = "RetailerOrders"

    OrderId = Column(Integer, primary_key=True, index=True)
    RetailerId = Column(Integer, nullable=False)
    DistributorId = Column(Integer, nullable=False)
    
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
    Amount = Column(Float, default=0.0)  # Total order amount including GST
    

    # Order state
    OrderStatus = Column(String, default="New")  # Pending, Cancelled, Completed

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
    
    Quantity = Column(Integer, nullable=False)

    GSTPercentage = Column(Float, nullable=False)    

    TotalAmount = Column(Float, nullable=False)      # (UnitPrice * Quantity) + GST
