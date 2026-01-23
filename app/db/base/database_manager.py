# app/database/base/database_manager.py

from ..base.database_factory import get_database
from ..base.idatabase import IDatabase
from typing import Any, Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_type: str):
        self.db: IDatabase = get_database(db_type)
        self._session = None  # for SQL: session; for Mongo: db handle

    async def connect(self) -> None:
        await self.db.connect()
        self._session = self.db.get_session()

    async def disconnect(self) -> None:
        await self.db.disconnect()
        self._session = None

    def get_session(self) -> Any:
        if not self._session:
            raise RuntimeError("Database session not initialized. Did you forget to connect?")
        return self._session

    # CRUD wrappers
    async def create(self, table_or_collection: Any, data: Dict) -> Any:
        return await self.db.create(table_or_collection, data)

    async def read(
        self, table_or_collection: Any, filters: Optional[Dict] = None) -> List[Any]:
        return await self.db.read(table_or_collection, filters)

    async def update(
        self, table_or_collection: Any, filters: Dict, updates: Dict) -> Any:
        return await self.db.update(table_or_collection, filters, updates)

    async def delete(self, table_or_collection: Any, filters: Dict) -> Any:
        return await self.db.delete(table_or_collection, filters)

    async def execute_query(self, raw_sql: str) -> Any:
        return await self.db.execute_query(raw_sql)
