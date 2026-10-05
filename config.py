from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    coingecko_plan: Literal["demo", "pro"] = "demo"
    coingecko_api_key: str = ""
    detail_concurrency: int = Field(default=3, ge=1)
    cache_ttl_seconds: int = Field(default=600, ge=0)

    # Filter thresholds (USD)
    max_fdv: float = 100_000_000
    min_volume_24h: float = 50_000
    min_tvl: float = 50_000

    @property
    def base_url(self) -> str:
        return (
            "https://pro-api.coingecko.com/api/v3"
            if self.coingecko_plan == "pro"
            else "https://api.coingecko.com/api/v3"
        )

    @property
    def auth_header(self) -> dict[str, str]:
        if not self.coingecko_api_key:
            return {}
        name = "x-cg-pro-api-key" if self.coingecko_plan == "pro" else "x-cg-demo-api-key"
        return {name: self.coingecko_api_key}


settings = Settings()