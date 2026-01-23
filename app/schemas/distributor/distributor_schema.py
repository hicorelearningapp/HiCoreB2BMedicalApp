from pydantic import BaseModel
from typing import Optional

class DistributorBase(BaseModel):
    CompanyName: Optional[str]
    ContactPersonName: Optional[str]
    GSTNumber: Optional[str]
    LicenseNumber: Optional[str]
    PhoneNumber: Optional[str]
    Email: Optional[str]

    # Address fields (same as Retailer)
    AddressLine1: str
    AddressLine2: Optional[str]
    City: str
    State: str
    Country: str
    PostalCode: str
    Latitude: Optional[float]
    Longitude: Optional[float]

    CompanyPicture: Optional[str]

    BankName: Optional[str]
    AccountNumber: Optional[str]
    IFSCCode: Optional[str]
    Branch: Optional[str]

    class Config:
        from_attributes = True


class DistributorCreate(DistributorBase):
    Email: str
    Password: str


class DistributorUpdate(DistributorBase):
    pass


class DistributorRead(DistributorBase):
    DistributorId: int
