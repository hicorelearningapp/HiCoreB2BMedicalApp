from sqlalchemy import Column, Integer, String, Float
from .sql_base import Base

class Distributor(Base):
    __tablename__ = "Distributor"

    DistributorId = Column(Integer, primary_key=True, index=True)
    CompanyName = Column(String, nullable=True)
    ContactPersonName = Column(String, nullable=True)
    GSTNumber = Column(String, nullable=True)
    LicenseNumber = Column(String, nullable=True)
    PhoneNumber = Column(String, nullable=True)
    Email = Column(String, nullable=True)
    PasswordHash = Column(String, nullable=True)

    # Address fields (same as Retailer)
    AddressLine1 = Column(String(255), nullable=True)
    AddressLine2 = Column(String(255), nullable=True)
    City = Column(String(100), nullable=True)
    State = Column(String(100), nullable=True)
    Country = Column(String(100), nullable=True)
    PostalCode = Column(String(20), nullable=True)
    Latitude = Column(Float, nullable=True)
    Longitude = Column(Float, nullable=True)

    CompanyPicture = Column(String, nullable=True)

    # Banking info
    BankName = Column(String, nullable=True)
    AccountNumber = Column(String, nullable=True)
    IFSCCode = Column(String, nullable=True)
    Branch = Column(String, nullable=True)
