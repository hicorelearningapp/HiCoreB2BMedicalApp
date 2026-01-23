from typing import List, Optional
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.retailer_model import Retailer
from ...schemas.retailer.retailer_schema import RetailerCreate, RetailerUpdate, RetailerRead
import hashlib

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
            obj = await self.db_manager.create(Retailer, data)
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
