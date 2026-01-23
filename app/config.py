from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    db_type: str = Field("sqlite", env="DP_TYPE")

    # Async-compatible database URLs
    sqlite_url: str = Field("sqlite+aiosqlite:///./medical.db", env="SQLITE_URL")
    postgresql_url: str = Field("postgresql+asyncpg://user:password@localhost/dbname", env="POSTGRESQL_URL")
    mysql_url: str = Field("mysql+aiomysql://user:password@localhost/dbname", env="MYSQL_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
