# app/database/base/idatabase.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class IDatabase(ABC):
    @abstractmethod
    async def connect(self) -> None:
        """Initialize connection / engine / client."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Tear down / close connection."""
        pass

    @abstractmethod
    def get_session(self) -> Any:
        """
        For SQL databases, this returns a session object (e.g. SQLAlchemy session).  
        For Mongo, returns a database / client handle.
        """
        pass

    @abstractmethod
    async def create(self, table_or_collection: Any, data: Dict) -> Any:
        pass

    @abstractmethod
    async def read(
        self, table_or_collection: Any, filters: Optional[Dict] = None) -> List[Dict]:
        pass

    @abstractmethod
    async def update(
        self, table_or_collection: Any, filters: Dict, updates: Dict) -> Any:
        pass

    @abstractmethod
    async def delete(
        self, table_or_collection: Any, filters: Dict) -> Any:
        pass

    @abstractmethod
    async def execute_query(self, raw_sql: str) -> Any:
        """
        For SQL DBs, run raw SQL. For Mongo, you may raise NotImplementedError or support aggregation.
        """
        pass
