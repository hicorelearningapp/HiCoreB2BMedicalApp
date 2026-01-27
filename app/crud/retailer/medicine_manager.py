from typing import List, Optional
from ...utils.logger import get_logger
from ...db.base.database_manager import DatabaseManager
from ...models.retailer.medicine_model import Medicine
from ...schemas.retailer.medicine_schema import MedicineCreate, MedicineUpdate, MedicineRead
import os

logger = get_logger(__name__)

class MedicineManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def create_medicine(self, medicine: MedicineCreate) -> dict:
        try:
            await self.db_manager.connect()
            data = medicine.dict()
            obj = await self.db_manager.create(Medicine, data)
            logger.info(f"Created medicine {obj.MedicineId}")
            return {
                "success": True,
                "message": "Medicine created successfully",
                "data": MedicineRead.from_orm(obj).dict()
            }
        except Exception as e:
            logger.error(f"Error creating medicine: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def get_medicine(self, medicine_id: int) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(Medicine, {"MedicineId": medicine_id})
            if result:
                return {
                    "success": True,
                    "message": "Medicine fetched successfully",
                    "data": MedicineRead.from_orm(result[0]).dict()
                }
            return {"success": False, "message": "Medicine not found", "data": None}
        except Exception as e:
            logger.error(f"Error fetching medicine {medicine_id}: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def get_all_medicines(self) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.read(Medicine)
            medicines = [MedicineRead.from_orm(m).dict() for m in result]
            return {"success": True, "message": "Medicines fetched successfully", "data": medicines}
        except Exception as e:
            logger.error(f"Error fetching medicines: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def update_medicine(self, medicine_id: int, data: MedicineUpdate) -> dict:
        try:
            await self.db_manager.connect()
            update_data = data.dict(exclude_unset=True)
            rowcount = await self.db_manager.update(Medicine, {"MedicineId": medicine_id}, update_data)
            if rowcount:
                logger.info(f"Updated medicine {medicine_id}, rows affected: {rowcount}")
                return {"success": True, "message": "Medicine updated successfully", "data": {"rows_affected": rowcount}}
            return {"success": False, "message": "Medicine not found or no changes made", "data": {"rows_affected": rowcount}}
        except Exception as e:
            logger.error(f"Error updating medicine {medicine_id}: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()

    async def delete_medicine(self, medicine_id: int) -> dict:
        try:
            await self.db_manager.connect()
            result = await self.db_manager.delete(Medicine, {"MedicineId": medicine_id})
            if result:
                logger.info(f"Deleted medicine {medicine_id}, rows affected: {result}")
                return {"success": True, "message": "Medicine deleted successfully", "data": {"rows_affected": result}}
            return {"success": False, "message": "Medicine not found", "data": {"rows_affected": result}}
        except Exception as e:
            logger.error(f"Error deleting medicine {medicine_id}: {e}")
            return {"success": False, "message": str(e)}
        finally:
            await self.db_manager.disconnect()
