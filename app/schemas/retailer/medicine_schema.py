from pydantic import BaseModel
from typing import Optional

class MedicineBase(BaseModel):
    MedicineName: str
    DosageForm: Optional[str]
    Strength: Optional[str]
    Manufacturer: Optional[str]
    PrescriptionRequired: Optional[bool] = False
    Size: Optional[str]
    UnitPrice: float
    TherapeuticClass: Optional[str]
    ImgUrl: Optional[str]
    
    class Config:
        from_attributes = True


class MedicineCreate(MedicineBase):
    pass  # No extra fields needed


class MedicineUpdate(MedicineBase):
    pass  # All fields optional when updating


class MedicineRead(MedicineBase):
    MedicineId: int
