from pydantic import BaseModel
from typing import Optional

class RetailerBase(BaseModel):
    ShopName: Optional[str]
    OwnerName: Optional[str]
    GSTNumber: Optional[str]
    LicenseNumber: Optional[str]
    PhoneNumber: Optional[str]
    Email: Optional[str]

    # Address
    AddressLine1: str
    AddressLine2: Optional[str]
    City: str
    State: str
    Country: str
    PostalCode: str
    Latitude: Optional[float]
    Longitude: Optional[float]

    ShopPic: Optional[str]

    # Banking info
    BankName: Optional[str]
    AccountNumber: Optional[str]
    IFSCCode: Optional[str]
    Branch: Optional[str]

    class Config:
        from_attributes = True


class RetailerCreate(RetailerBase):
    Email: str
    Password: str  # plain password input for creation


class RetailerUpdate(RetailerBase):
    pass


class RetailerRead(RetailerBase):
    RetailerId: int
