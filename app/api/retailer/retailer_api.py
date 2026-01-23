import os
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from typing import List
from ...config import settings
from ...schemas.retailer.retailer_schema import RetailerCreate, RetailerUpdate, RetailerRead
from ...crud.retailer.retailer_manager import RetailerManager
from ...utils.image_uploader import save_picture


class RetailerAPI:
    def __init__(self):
        self.router = APIRouter()
        self.crud = RetailerManager(settings.db_type)
        self.register_routes()

    def register_routes(self):
        self.router.post("/retailers", response_model=dict)(self.create_retailer)
        self.router.get("/retailers/{retailer_id}", response_model=dict)(self.get_retailer)
        self.router.get("/retailers", response_model=dict)(self.get_all_retailers)
        self.router.put("/retailers/{retailer_id}", response_model=dict)(self.update_retailer)
        self.router.delete("/retailers/{retailer_id}", response_model=dict)(self.delete_retailer)

    # ---------------- CREATE ----------------
    async def create_retailer(
        self,
        ShopName: str = Form(...),
        OwnerName: str = Form(...),
        GSTNumber: str = Form(None),
        LicenseNumber: str = Form(None),
        PhoneNumber: str = Form(None),
        Email: str = Form(...),
        Password: str = Form(...),
        AddressLine1: str = Form(...),
        AddressLine2: str = Form(None),
        City: str = Form(...),
        State: str = Form(...),
        Country: str = Form(...),
        PostalCode: str = Form(...),
        Latitude: float = Form(None),
        Longitude: float = Form(None),
        BankName: str = Form(None),
        AccountNumber: str = Form(None),
        IFSCCode: str = Form(None),
        Branch: str = Form(None),
        ShopPic: UploadFile = File(None),
    ):
        try:
            # save image if provided
            shop_pic_path = None
            if ShopPic:
                shop_pic_path = await save_picture(ShopPic, "Shop")

            # Build RetailerCreate object
            retailer_obj = RetailerCreate(
                ShopName=ShopName,
                OwnerName=OwnerName,
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
                ShopPic=shop_pic_path,
            )

            return await self.crud.create_retailer(retailer_obj)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- GET ----------------
    async def get_retailer(self, retailer_id: int):
        try:
            result = await self.crud.get_retailer(retailer_id)
            if not result["success"]:
                raise HTTPException(status_code=404, detail=result.get("message", "Retailer not found"))
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_retailers(self):
        try:
            return await self.crud.get_all_retailers()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- UPDATE ----------------
    async def update_retailer(
        self,
        retailer_id: int,
        ShopName: str = Form(None),
        OwnerName: str = Form(None),
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
        ShopPic: UploadFile = File(None),
    ):
        try:
            old_retailer = await self.crud.get_retailer(retailer_id)
            if not old_retailer["success"]:
                raise HTTPException(status_code=404, detail="Retailer not found")

            update_data = {}

            # Update all text fields
            for field_name, value in {
                "ShopName": ShopName,
                "OwnerName": OwnerName,
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
                    if field_name == "Password":
                        update_data["PasswordHash"] = value
                    else:
                        update_data[field_name] = value

            # Handle shop picture replacement
            if ShopPic:
                new_path = await save_picture(ShopPic, "Shop")

                old_path = old_retailer["data"]["ShopPic"]
                if old_path:
                    abs_old_path = os.path.normpath(os.path.join(os.getcwd(), old_path))
                    if os.path.exists(abs_old_path):
                        os.remove(abs_old_path)
                        print(f"Deleted old shop image: {abs_old_path}")
                    else:
                        print(f"Old shop image does not exist: {abs_old_path}")

                update_data["ShopPic"] = new_path

            return await self.crud.update_retailer(retailer_id, RetailerUpdate(**update_data))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ---------------- DELETE ----------------
    async def delete_retailer(self, retailer_id: int):
        try:
            retailer = await self.crud.get_retailer(retailer_id)
            if not retailer["success"]:
                raise HTTPException(status_code=404, detail="Retailer not found")

            image_path = retailer["data"]["ShopPic"]

            # Delete from DB
            result = await self.crud.delete_retailer(retailer_id)

            # Delete physical file
            if image_path:
                abs_path = os.path.normpath(os.path.join(os.getcwd(), image_path))
                if os.path.exists(abs_path):
                    os.remove(abs_path)
                    print(f"Deleted shop image: {abs_path}")
                else:
                    print(f"Shop image does not exist: {abs_path}")

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
