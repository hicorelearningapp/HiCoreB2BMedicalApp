from sqlalchemy import Column, Integer, String, Boolean, DateTime
from ...utils.timezone import ist_now
from .sql_base import Base


class DistributorNotification(Base):
    __tablename__ = "DistributorNotification"

    NotificationId = Column(Integer, primary_key=True, index=True)
    DistributorId = Column(Integer, nullable=False)

    Title = Column(String, nullable=False)
    Message = Column(String, nullable=False)
    Type = Column(String, nullable=False)  # e.g., "Order", "Stock", "System"
    IsRead = Column(Boolean, default=False)

    Date = Column(DateTime, default=ist_now)
    CreatedAt = Column(DateTime, default=ist_now)
