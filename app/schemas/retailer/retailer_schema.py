from pydantic import BaseModel, EmailStr
from typing import Optional

class RetailerBase(BaseModel):
    ShopName: Optional[str] = None
    OwnerName: Optional[str] = None
    GSTNumber: Optional[str] = None
    LicenseNumber: Optional[str] = None
    PhoneNumber: Optional[str] = None
    Email: Optional[str] = None
    

    # Address
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    PostalCode: Optional[str] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None

    ShopPic: Optional[str] = None

    # Banking info
    BankName: Optional[str] = None
    AccountNumber: Optional[str] = None
    IFSCCode: Optional[str] = None
    Branch: Optional[str] = None

    IsRegistered: Optional[bool] = None

    class Config:
        from_attributes = True


class RetailerCreate(RetailerBase):
    Email: str
    Password: str  # plain password input for creation


class RetailerUpdate(RetailerBase):
    Password: Optional[str] = None


class RetailerRead(RetailerBase):
    RetailerId: int
    # PasswordHash: Optional[str]


class RetailerRegisterSchema(BaseModel):
    Email: str
    Password: str

class RetailerLoginSchema(BaseModel):
    Email: str
    Password: str