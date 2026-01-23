# app/database/base/database_factory.py

from ...config import settings
from ..sql.postgres_database import PostgresDatabase
from ..sql.mysql_database import MySQLDatabase
from ..sql.sql_database import SQLiteDatabase
from ..nosql.mongodb_database import MongoDBDatabase
from ..base.idatabase import IDatabase

def get_database(db_type: str) -> IDatabase:
    db_type = db_type.lower()
    if db_type in ("postgresql", "postgres"):
        return PostgresDatabase(settings.postgresql_url)
    elif db_type == "mysql":
        return MySQLDatabase(settings.mysql_url)
    elif db_type in ("sqlite", "sqlite3"):
        return SQLiteDatabase(settings.sqlite_url)
    elif db_type in ("mongodb", "mongo"):
        return MongoDBDatabase(settings.mongodb_uri, settings.mongodb_dbname)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
