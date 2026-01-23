# app/database/sql/mysql_database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import Any, Dict, List, Optional

from ..base.idatabase import IDatabase


class MySQLDatabase(IDatabase):
    def __init__(self, db_url: str):
        # e.g. "mysql+aiomysql://user:pass@host:port/dbname"
        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None

    async def connect(self) -> None:
        self.engine = create_async_engine(self.db_url, future=True, echo=False)
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def disconnect(self) -> None:
        if self.engine:
            await self.engine.dispose()
            self.engine = None

    def get_session(self) -> AsyncSession:
        if not self.SessionLocal:
            raise RuntimeError("Database not connected")
        return self.SessionLocal()

    async def create(self, table_or_collection: Any, data: Dict) -> Any:
        session = self.get_session()
        obj = table_or_collection(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def read(
        self, table_or_collection: Any, filters: Optional[Dict] = None) -> List[Any]:
        session = self.get_session()
        query = session.query(table_or_collection)
        if filters:
            for k, v in filters.items():
                query = query.filter(getattr(table_or_collection, k) == v)
        result = await session.execute(query)
        return result.scalars().all()

    async def update(
        self, table_or_collection: Any, filters: Dict, updates: Dict) -> int:
        session = self.get_session()
        query = session.query(table_or_collection)
        for k, v in filters.items():
            query = query.filter(getattr(table_or_collection, k) == v)
        res = await session.execute(query.update(updates))
        await session.commit()
        return res.rowcount

    async def delete(
        self, table_or_collection: Any, filters: Dict) -> int:
        session = self.get_session()
        query = session.query(table_or_collection)
        for k, v in filters.items():
            query = query.filter(getattr(table_or_collection, k) == v)
        res = await session.execute(query.delete())
        await session.commit()
        return res.rowcount

    async def execute_query(self, raw_sql: str) -> Any:
        session = self.get_session()
        result = await session.execute(text(raw_sql))
        return result.fetchall()
