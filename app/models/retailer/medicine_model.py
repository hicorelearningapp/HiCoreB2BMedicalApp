from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from .sql_base import Base

class Medicine(Base):
    __tablename__ = "Medicine"

    MedicineId = Column(Integer, primary_key=True, index=True)
    MedicineName = Column(String, nullable=False)
    GenericName = Column(String, nullable=True)
    DosageForm = Column(String, nullable=True)
    Strength = Column(String, nullable=True)
    Manufacturer = Column(String, nullable=True)
    PrescriptionRequired = Column(Boolean, default=False)
    Size = Column(String, nullable=True)
    UnitPrice = Column(Float, nullable=False)
    TherapeuticClass = Column(String, nullable=True)
    ImgUrl = Column(String, nullable=True)
    MedicineCategoryId = Column(Integer, nullable=True)  # Optional FK if you have a category table
