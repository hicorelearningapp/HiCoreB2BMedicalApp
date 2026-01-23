# app/database/mongodb_database.py

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

from ..base.idatabase import IDatabase


class MongoDBDatabase(IDatabase):
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    async def connect(self) -> None:
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()

    def get_session(self) -> Any:
        if not self.db:
            raise RuntimeError("MongoDB not connected")
        return self.db

    async def create(self, collection_name: str, data: Dict) -> Any:
        coll = self.db[collection_name]
        res = await coll.insert_one(data)
        return {"inserted_id": res.inserted_id}

    async def read(
        self, collection_name: str, filters: Optional[Dict] = None) -> List[Dict]:
        coll = self.db[collection_name]
        cursor = coll.find(filters or {})
        docs = await cursor.to_list(length=100)  # or more or customizable
        return docs

    async def update(
        self, collection_name: str, filters: Dict, updates: Dict) -> Any:
        coll = self.db[collection_name]
        res = await coll.update_many(filters, {"$set": updates})
        return {"matched_count": res.matched_count, "modified_count": res.modified_count}

    async def delete(self, collection_name: str, filters: Dict) -> Any:
        coll = self.db[collection_name]
        res = await coll.delete_many(filters)
        return {"deleted_count": res.deleted_count}

    async def execute_query(self, raw_sql: str) -> Any:
        raise NotImplementedError("Raw SQL not supported in MongoDB backend")
