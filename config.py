from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DatabaseConfig(BaseModel):
    url: str = "postgresql+asyncpg://user:password@pg:5432/auth_system"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class AuthConfig(BaseModel):
    secret_key: str = "super-secret-key"
    algorithm: str = "HS256"
    ACCESS_EXPIRE_MINUTES: int = 30
    REFRESH_EXPIRE_DAYS: int = 7


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig = DatabaseConfig()
    auth: AuthConfig = AuthConfig()


settings = Settings()
