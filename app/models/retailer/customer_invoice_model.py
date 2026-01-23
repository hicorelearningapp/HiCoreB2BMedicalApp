from sqlalchemy import Column, Integer, String, Float, DateTime
from ...utils.timezone import ist_now
from .sql_base import Base


class CustomerInvoice(Base):
    __tablename__ = "CustomerInvoice"

    InvoiceId = Column(Integer, primary_key=True, index=True)
    OrderId = Column(Integer, nullable=False)   # linked to CustomerOrder
    RetailerId = Column(Integer, nullable=False)  # link to retailer
    CustomerName = Column(String, nullable=False)

    InvoiceDate = Column(DateTime, default=ist_now)
    DueDate = Column(DateTime, nullable=True)
    TotalAmount = Column(Float, nullable=True)
    TaxAmount = Column(Float, default=0.0)
    DiscountAmount = Column(Float, default=0.0)
    NetAmount = Column(Float, nullable=True)

    PaymentStatus = Column(String, default="Pending")  # Pending / Paid / Overdue
    PaymentMode = Column(String, nullable=True)
    PaymentTransactionId = Column(String, nullable=True)

    CreatedAt = Column(DateTime, default=ist_now)
    UpdatedAt = Column(DateTime, default=ist_now, onupdate=ist_now)
    CreatedBy = Column(String, nullable=True)
    UpdatedBy = Column(String, nullable=True)


class CustomerInvoiceItem(Base):
    __tablename__ = "CustomerInvoiceItem"

    ItemId = Column(Integer, primary_key=True, index=True)
    InvoiceId = Column(Integer, nullable=False)
    OrderId = Column(Integer, nullable=False)
    RetailerId = Column(Integer, nullable=False)

    MedicineName = Column(String, nullable=False)
    Brand = Column(String, nullable=True)
    Quantity = Column(Integer, nullable=False)
    Price = Column(Float, nullable=True)
    TotalAmount = Column(Float, nullable=True)

    CreatedAt = Column(DateTime, default=ist_now)
