import os
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from ...config import settings
from ...schemas.distributor.distributor_schema import (
    DistributorCreate,
    DistributorUpdate,
    DistributorRegisterSchema,
    DistributorLoginSchema
)
from ...crud.distributor.distributor_manager import DistributorManager
from ...utils.image_uploader import save_picture


class DistributorAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = DistributorManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/distributors", response_model=dict)(self.create_distributor)
        self.router.get("/distributors/{distributor_id}", response_model=dict)(self.get_distributor)
        self.router.get("/distributors", response_model=dict)(self.get_all_distributors)
        self.router.put("/distributors/{distributor_id}", response_model=dict)(self.update_distributor)
        self.router.delete("/distributors/{distributor_id}", response_model=dict)(self.delete_distributor)
        self.router.post("/distributors/register", response_model=dict)(self.register)
        self.router.post("/distributors/login", response_model=dict)(self.login)


    # ---------------- CREATE ----------------
    async def create_distributor(
        self,
        CompanyName: str = Form(None),
        ContactPersonName: str = Form(None),
        GSTNumber: str = Form(None),
        LicenseNumber: str = Form(None),
        PhoneNumber: str = Form(None),
        Email: str = Form(None),
        Password: str = Form(None),
        AddressLine1: str = Form(None),
        AddressLine2: str = Form(None),
        City: str = Form(None),
        State: str = Form(None),
        Country: str = Form(None),
        PostalCode: str = Form(None),
        Latitude: float = Form(None),
        Longitude: float = Form(None),
        BankName: str = Form(None),
        AccountNumber: str = Form(None),
        IFSCCode: str = Form(None),
        Branch: str = Form(None),
        CompanyPicture: UploadFile = File(None),
    ):
        try:
            company_pic_path = None
            if CompanyPicture:
                company_pic_path = await save_picture(CompanyPicture, "CompanyPic")

            distributor_obj = DistributorCreate(
                CompanyName=CompanyName,
                ContactPersonName=ContactPersonName,
                GSTNumber=GSTNumber,
                LicenseNumber=LicenseNumber,
                PhoneNumber=PhoneNumber,
                Email=Email,
                Password=Password,
                AddressLine1=AddressLine1,
                AddressLine2=AddressLine2,
                City=City,
                State=State,
                Country=Country,
                PostalCode=PostalCode,
                Latitude=Latitude,
                Longitude=Longitude,
                BankName=BankName,
                AccountNumber=AccountNumber,
                IFSCCode=IFSCCode,
                Branch=Branch,
                CompanyPicture=company_pic_path,
            )

            return await self.crud.create_distributor(distributor_obj)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- GET ----------------
    async def get_distributor(self, distributor_id: int):
        try:
            result = await self.crud.get_distributor(distributor_id)
            if not result["success"]:
                raise HTTPException(status_code=404, detail=result.get("message", "Distributor not found"))
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_distributors(self):
        try:
            return await self.crud.get_all_distributors()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- UPDATE ----------------
    async def update_distributor(
        self,
        distributor_id: int,
        CompanyName: str = Form(None),
        ContactPersonName: str = Form(None),
        GSTNumber: str = Form(None),
        LicenseNumber: str = Form(None),
        PhoneNumber: str = Form(None),
        Email: str = Form(None),
        Password: str = Form(None),
        AddressLine1: str = Form(None),
        AddressLine2: str = Form(None),
        City: str = Form(None),
        State: str = Form(None),
        Country: str = Form(None),
        PostalCode: str = Form(None),
        Latitude: float = Form(None),
        Longitude: float = Form(None),
        BankName: str = Form(None),
        AccountNumber: str = Form(None),
        IFSCCode: str = Form(None),
        Branch: str = Form(None),
        CompanyPicture: UploadFile = File(None),
    ):
        try:
            old_distributor = await self.crud.get_distributor(distributor_id)
            if not old_distributor["success"]:
                raise HTTPException(status_code=404, detail="Distributor not found")

            update_data = {}

            for field_name, value in {
                "CompanyName": CompanyName,
                "ContactPersonName": ContactPersonName,
                "GSTNumber": GSTNumber,
                "LicenseNumber": LicenseNumber,
                "PhoneNumber": PhoneNumber,
                "Email": Email,
                "Password": Password,
                "AddressLine1": AddressLine1,
                "AddressLine2": AddressLine2,
                "City": City,
                "State": State,
                "Country": Country,
                "PostalCode": PostalCode,
                "Latitude": Latitude,
                "Longitude": Longitude,
                "BankName": BankName,
                "AccountNumber": AccountNumber,
                "IFSCCode": IFSCCode,
                "Branch": Branch,
            }.items():
                if value is not None:
                    update_data[field_name] = value
                        

            # Handle company picture
            if CompanyPicture:
                new_path = await save_picture(CompanyPicture, "CompanyPic")

                old_path = old_distributor["data"]["CompanyPicture"]
                if old_path:
                    abs_old_path = os.path.normpath(os.path.join(os.getcwd(), old_path))
                    if os.path.exists(abs_old_path):
                        os.remove(abs_old_path)
                        print(f"Deleted old company image: {abs_old_path}")
                    else:
                        print(f"Old company image does not exist: {abs_old_path}")

                update_data["CompanyPicture"] = new_path

            return await self.crud.update_distributor(distributor_id, DistributorUpdate(**update_data))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- DELETE ----------------
    async def delete_distributor(self, distributor_id: int):
        try:
            distributor = await self.crud.get_distributor(distributor_id)
            if not distributor["success"]:
                raise HTTPException(status_code=404, detail="Distributor not found")

            image_path = distributor["data"]["CompanyPicture"]

            result = await self.crud.delete_distributor(distributor_id)

            if image_path:
                abs_path = os.path.normpath(os.path.join(os.getcwd(), image_path))
                if os.path.exists(abs_path):
                    os.remove(abs_path)
                    print(f"Deleted company image: {abs_path}")
                else:
                    print(f"Company image does not exist: {abs_path}")

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    # ---------------- REGISTER ----------------
    async def register(self, payload: DistributorRegisterSchema):
        result = await self.crud.register(payload.Email, payload.Password)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result

    # ---------------- LOGIN ----------------
    async def login(self, payload: DistributorLoginSchema):
        result = await self.crud.login(payload.Email, payload.Password)
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["message"])
        return result
