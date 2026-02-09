from pydantic import BaseModel, EmailStr
from typing import Optional

class DistributorBase(BaseModel):
    CompanyName: Optional[str] = None
    ContactPersonName: Optional[str] = None
    GSTNumber: Optional[str] = None
    LicenseNumber: Optional[str] = None
    PhoneNumber: Optional[str] = None
    Email: Optional[str] = None

    # Address fields (same as Retailer)
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    PostalCode: Optional[str] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None

    CompanyPicture: Optional[str] = None

    BankName: Optional[str] = None
    AccountNumber: Optional[str] = None
    IFSCCode: Optional[str] = None
    Branch: Optional[str] = None

    class Config:
        from_attributes = True


class DistributorCreate(DistributorBase):
    Email: str
    Password: str


class DistributorUpdate(DistributorBase):
    Password: Optional[str] = None


class DistributorRead(DistributorBase):
    DistributorId: int
    # PasswordHash: Optional[str]


# ---------------- SCHEMAS ----------------
class DistributorRegisterSchema(BaseModel):
    Email: str
    Password: str

class DistributorLoginSchema(BaseModel):
    Email: str
    Password: str