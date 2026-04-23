from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./tasks.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rate_limit_per_minute: int = 100

    model_config = {"env_file": ".env"}


settings = Settings()
