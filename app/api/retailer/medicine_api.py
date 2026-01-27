import os
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from ...config import settings
from ...schemas.retailer.medicine_schema import MedicineCreate, MedicineUpdate
from ...crud.retailer.medicine_manager import MedicineManager
from ...utils.image_uploader import save_picture

class MedicineAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = MedicineManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/medicines", response_model=dict)(self.create_medicine)
        self.router.get("/medicines/{medicine_id}", response_model=dict)(self.get_medicine)
        self.router.get("/medicines", response_model=dict)(self.get_all_medicines)
        self.router.put("/medicines/{medicine_id}", response_model=dict)(self.update_medicine)
        self.router.delete("/medicines/{medicine_id}", response_model=dict)(self.delete_medicine)

    # ---------------- CREATE ----------------
    async def create_medicine(
        self,
        MedicineName: str = Form(...),
        GenericName: str = Form(None),
        DosageForm: str = Form(None),
        Strength: str = Form(None),
        Manufacturer: str = Form(None),
        PrescriptionRequired: bool = Form(False),
        Size: str = Form(None),
        UnitPrice: float = Form(...),
        TherapeuticClass: str = Form(None),
        MedicineCategoryId: int = Form(None),
        ImgUrl: UploadFile = File(None)
    ):
        try:
            img_path = None
            if ImgUrl:
                img_path = await save_picture(ImgUrl, "Medicine")

            medicine_obj = MedicineCreate(
                MedicineName=MedicineName,
                GenericName=GenericName,
                DosageForm=DosageForm,
                Strength=Strength,
                Manufacturer=Manufacturer,
                PrescriptionRequired=PrescriptionRequired,
                Size=Size,
                UnitPrice=UnitPrice,
                TherapeuticClass=TherapeuticClass,
                MedicineCategoryId=MedicineCategoryId,
                ImgUrl=img_path
            )
            return await self.crud.create_medicine(medicine_obj)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- GET ----------------
    async def get_medicine(self, medicine_id: int):
        result = await self.crud.get_medicine(medicine_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("message", "Medicine not found"))
        return result

    async def get_all_medicines(self):
        return await self.crud.get_all_medicines()

    # ---------------- UPDATE ----------------
    async def update_medicine(
        self,
        medicine_id: int,
        MedicineName: str = Form(None),
        GenericName: str = Form(None),
        DosageForm: str = Form(None),
        Strength: str = Form(None),
        Manufacturer: str = Form(None),
        PrescriptionRequired: bool = Form(None),
        Size: str = Form(None),
        UnitPrice: float = Form(None),
        TherapeuticClass: str = Form(None),
        MedicineCategoryId: int = Form(None),
        ImgUrl: UploadFile = File(None)
    ):
        try:
            old_medicine = await self.crud.get_medicine(medicine_id)
            if not old_medicine["success"]:
                raise HTTPException(status_code=404, detail="Medicine not found")

            update_data = {}
            for field, value in {
                "MedicineName": MedicineName,
                "GenericName": GenericName,
                "DosageForm": DosageForm,
                "Strength": Strength,
                "Manufacturer": Manufacturer,
                "PrescriptionRequired": PrescriptionRequired,
                "Size": Size,
                "UnitPrice": UnitPrice,
                "TherapeuticClass": TherapeuticClass,
                "MedicineCategoryId": MedicineCategoryId
            }.items():
                if value is not None:
                    update_data[field] = value

            # Handle image replacement
            if ImgUrl:
                new_path = await save_picture(ImgUrl, "Medicine")
                old_path = old_medicine["data"]["ImgUrl"]
                if old_path and os.path.exists(old_path):
                    os.remove(old_path)
                update_data["ImgUrl"] = new_path

            return await self.crud.update_medicine(medicine_id, MedicineUpdate(**update_data))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- DELETE ----------------
    async def delete_medicine(self, medicine_id: int):
        try:
            medicine = await self.crud.get_medicine(medicine_id)
            if not medicine["success"]:
                raise HTTPException(status_code=404, detail="Medicine not found")

            image_path = medicine["data"]["ImgUrl"]
            result = await self.crud.delete_medicine(medicine_id)

            # Delete image file
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
