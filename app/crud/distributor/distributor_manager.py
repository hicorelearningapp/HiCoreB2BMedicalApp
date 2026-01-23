from typing import Optional
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.distributor.distributor_model import Distributor
from ...schemas.distributor.distributor_schema import (
    DistributorCreate,
    DistributorUpdate,
    DistributorRead
)
import hashlib

logger = get_logger(__name__)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class DistributorManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def create_distributor(self, distributor: DistributorCreate) -> dict:
        try:
            await self.db_manager.connect()
            data = distributor.dict()
            data["PasswordHash"] = hash_password(data.pop("Password"))
            obj = await self.db_manager.create(Distributor, data)
            logger.info(f"Created distributor {obj.DistributorId}")
            return {
                "success": True,
                "message": "Distributor created successfully",
                "data": DistributorRead.from_orm(obj).dict()
            }
        except Exception as e:
            logger.error(f"Error creating distributor: {e}")
            return {"success": False, "message": f"Error creating distributor: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def get_distributor(self, distributor_id: int) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(Distributor, {"DistributorId": distributor_id})
            if result:
                return {
                    "success": True,
                    "message": "Distributor fetched successfully",
                    "data": DistributorRead.from_orm(result[0]).dict()
                }
            return {"success": False, "message": "Distributor not found", "data": None}
        except Exception as e:
            logger.error(f"Error fetching distributor: {e}")
            return {"success": False, "message": f"Error fetching distributor: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def get_all_distributors(self) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(Distributor)
            distributors = [DistributorRead.from_orm(r).dict() for r in result]
            return {
                "success": True,
                "message": "Distributors fetched successfully",
                "data": distributors
            }
        except Exception as e:
            logger.error(f"Error fetching distributors: {e}")
            return {"success": False, "message": f"Error fetching distributors: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def update_distributor(self, distributor_id: int, data: DistributorUpdate) -> dict:
        try:
            await self.db_manager.connect()
            update_data = data.dict(exclude_unset=True)

            if "Password" in update_data:
                update_data["PasswordHash"] = hash_password(update_data.pop("Password"))

            rowcount = await self.db_manager.update(
                Distributor, {"DistributorId": distributor_id}, update_data
            )
            return {
                "success": bool(rowcount),
                "message": "Distributor updated successfully" if rowcount else "Distributor not found",
                "data": {"rows_affected": rowcount}
            }
        except Exception as e:
            logger.error(f"Error updating distributor: {e}")
            return {"success": False, "message": f"Error updating distributor: {e}"}
        finally:
            await self.db_manager.disconnect()

    async def delete_distributor(self, distributor_id: int) -> dict:
        try:
            await self.db_manager.connect()
            rowcount = await self.db_manager.delete(Distributor, {"DistributorId": distributor_id})
            return {
                "success": bool(rowcount),
                "message": "Distributor deleted successfully" if rowcount else "Distributor not found",
                "data": {"rows_affected": rowcount}
            }
        except Exception as e:
            logger.error(f"Error deleting distributor: {e}")
            return {"success": False, "message": f"Error deleting distributor: {e}"}
        finally:
            await self.db_manager.disconnect()
