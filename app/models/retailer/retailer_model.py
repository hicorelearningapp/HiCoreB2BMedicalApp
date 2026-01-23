from sqlalchemy import Column, Integer, String, Float
from .sql_base import Base

class Retailer(Base):
    __tablename__ = "Retailer"

    RetailerId = Column(Integer, primary_key=True, index=True)
    ShopName = Column(String, nullable=True)
    OwnerName = Column(String, nullable=True)
    GSTNumber = Column(String, nullable=True)
    LicenseNumber = Column(String, nullable=True)
    PhoneNumber = Column(String, nullable=True)
    Email = Column(String, nullable=True)
    PasswordHash = Column(String, nullable=True)  # Store hashed password

    # Address fields
    AddressLine1 = Column(String(255), nullable=False)
    AddressLine2 = Column(String(255), nullable=True)
    City = Column(String(100), nullable=False)
    State = Column(String(100), nullable=False)
    Country = Column(String(100), nullable=False)
    PostalCode = Column(String(20), nullable=False)
    Latitude = Column(Float, nullable=True)
    Longitude = Column(Float, nullable=True)

    ShopPic = Column(String, nullable=True)

    # Banking info
    BankName = Column(String, nullable=True)
    AccountNumber = Column(String, nullable=True)
    IFSCCode = Column(String, nullable=True)
    Branch = Column(String, nullable=True)
