from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    coinpaprika_base_url: str = "https://api.coinpaprika.com/v1"
    cache_ttl_seconds: int = Field(default=600, ge=0)
    max_fdv: float = 100_000_000
    min_volume_24h: float = 50_000


settings = Settings()