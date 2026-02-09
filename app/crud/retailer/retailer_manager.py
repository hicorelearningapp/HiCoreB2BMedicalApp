from typing import List, Optional
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_model import Retailer
from ...schemas.retailer.retailer_schema import RetailerCreate, RetailerUpdate, RetailerRead
import hashlib
from ...utils.retailer_sync import sync_retailer


logger = get_logger(__name__)

def hash_password(password: str) -> str:
    """Simple SHA256 hash. Replace with your secure hashing method."""
    return hashlib.sha256(password.encode()).hexdigest()


class RetailerManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def create_retailer(self, retailer: RetailerCreate) -> dict:
        try:
            await self.db_manager.connect()
            data = retailer.dict()
            data["PasswordHash"] = hash_password(data.pop("Password"))
            existing = await self.db_manager.read(Retailer, {"Email": data["Email"]})
            if not existing:
                obj = await self.db_manager.create(Retailer, data)
            else:
                return {
                "success": False,
                "message": "Email Id Already Exists"
            }
            # 🔁 SYNC
            res = await sync_retailer(
                "create",
                RetailerRead.from_orm(obj).dict()
            )
            print(res)
            logger.info(f"Created retailer {obj.RetailerId}")
            return {
                "success": True,
                "message": "Retailer created successfully",
                "data": RetailerRead.from_orm(obj).dict()
            }
        except Exception as e:
            logger.error(f"Error creating retailer: {e}")
            return {"success": False, "message": f"Error creating retailer: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def get_retailer(self, retailer_id: int) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(Retailer, {"RetailerId": retailer_id})
            if result:
                return {
                    "success": True,
                    "message": "Retailer fetched successfully",
                    "data": RetailerRead.from_orm(result[0]).dict()
                }
            return {"success": False, "message": "Retailer not found", "data": None}
        except Exception as e:
            logger.error(f"Error fetching retailer {retailer_id}: {e}")
            return {"success": False, "message": f"Error fetching retailer: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def get_all_retailers(self) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(Retailer)
            retailers = [RetailerRead.from_orm(r).dict() for r in result]
            return {
                "success": True,
                "message": "Retailers fetched successfully",
                "data": retailers
            }
        except Exception as e:
            logger.error(f"Error fetching retailers: {e}")
            return {"success": False, "message": f"Error fetching retailers: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def update_retailer(self, retailer_id: int, data: RetailerUpdate) -> dict:
        try:
            await self.db_manager.connect()
            update_data = data.dict(exclude_unset=True)
            if "Password" in update_data:
                update_data["PasswordHash"] = hash_password(update_data.pop("Password"))
            rowcount = await self.db_manager.update(
                Retailer, {"RetailerId": retailer_id}, update_data
            )
            if rowcount:

                # 🔁 SYNC
                await sync_retailer(
                    "update",
                    {
                        "RetailerId": retailer_id,
                        **update_data
                    }
                )


                logger.info(f"Updated retailer {retailer_id}, rows affected: {rowcount}")
                return {
                    "success": True,
                    "message": "Retailer updated successfully",
                    "data": {"rows_affected": rowcount}
                }
            return {
                "success": False,
                "message": "Retailer not found or no changes made",
                "data": {"rows_affected": rowcount}
            }
        except Exception as e:
            logger.error(f"Error updating retailer {retailer_id}: {e}")
            return {"success": False, "message": f"Error updating retailer: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def delete_retailer(self, retailer_id: int) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.delete(Retailer, {"RetailerId": retailer_id})
            if rowcount:

                # 🔁 SYNC
                await sync_retailer(
                    "delete",
                    {"RetailerId": retailer_id}
                )

                logger.info(f"Deleted retailer {retailer_id}, rows affected: {rowcount}")
                return {
                    "success": True,
                    "message": "Retailer deleted successfully",
                    "data": {"rows_affected": rowcount}
                }
            return {
                "success": False,
                "message": "Retailer not found",
                "data": {"rows_affected": rowcount}
            }
        except Exception as e:
            logger.error(f"Error deleting retailer {retailer_id}: {e}")
            return {"success": False, "message": f"Error deleting retailer: {e}"}
        finally:
            await self.db_manager.disconnect()


    # ---------------- REGISTER ----------------
    async def register(self, email: str, password: str) -> dict:
        await self.db_manager.connect()
        try:
            # Check if email already exists
            existing = await self.db_manager.read(Retailer, {"Email": email})
            if existing:
                return {"success": False, "message": "Email already registered"}

            retailer = await self.db_manager.create(
                Retailer,
                {
                    "Email": email,
                    "PasswordHash": hash_password(password),
                },
            )

            # 🔁 SYNC
            await sync_retailer(
                "register",
                {
                    "RetailerId": retailer.RetailerId,
                    "Email": retailer.Email,
                    "PasswordHash": retailer.PasswordHash,
                }
            )

            return {
                "success": True,
                "message": "Registered successfully",
                "data": {"RetailerId": retailer.RetailerId, "Email": retailer.Email},
            }

        except Exception as e:
            logger.error(f"Error registering retailer: {e}")
            return {"success": False, "message": f"Error registering retailer: {e}"}
        finally:
            await self.db_manager.disconnect()

    # ---------------- LOGIN ----------------
    async def login(self, email: str, password: str) -> dict:
        await self.db_manager.connect()
        try:
            result = await self.db_manager.read(Retailer, {"Email": email})
            if not result:
                return {"success": False, "message": "Invalid credentials"}

            retailer = result[0]
            if retailer.PasswordHash != hash_password(password):
                return {"success": False, "message": "Invalid credentials"}

            return {
                "success": True,
                "message": "Login successful",
                "data": {"RetailerId": retailer.RetailerId, "Email": retailer.Email},
            }

        except Exception as e:
            logger.error(f"Error logging in retailer: {e}")
            return {"success": False, "message": f"Error logging in retailer: {e}"}
        finally:
            await self.db_manager.disconnect()