from sqlalchemy import Column, Integer, String, Float, DateTime
from ...utils.timezone import ist_now
from .sql_base import Base


class PharmaOrder(Base):
    __tablename__ = "PharmaOrder"

    PONumber = Column(Integer, primary_key=True, index=True)
    DistributorId = Column(Integer, nullable=False)
    PharmaId = Column(Integer, nullable=False)  # 🔁 changed from PharmaName

    OrderDate = Column(DateTime, default=ist_now)
    ExpectedDelivery = Column(DateTime, nullable=True)

    TotalItems = Column(Integer, nullable=True)
    TotalAmount = Column(Float, nullable=True)

    Status = Column(String, default="Placed")  # Placed / InTransit / Delivered / Cancelled

    CreatedAt = Column(DateTime, default=ist_now)
    UpdatedAt = Column(DateTime, default=ist_now, onupdate=ist_now)


class PharmaOrderItem(Base):
    __tablename__ = "PharmaOrderItem"

    ItemId = Column(Integer, primary_key=True, index=True)
    PONumber = Column(Integer, nullable=False)
    DistributorId = Column(Integer, nullable=False)

    MedicineName = Column(String, nullable=False)
    Brand = Column(String, nullable=True)
    Quantity = Column(Integer, nullable=False)
    Price = Column(Float, nullable=True)
    TotalAmount = Column(Float, nullable=True)
    Batch = Column(String, nullable=True)
    ExpiryDate = Column(DateTime, nullable=True)

    CreatedAt = Column(DateTime, default=ist_now)
