import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx

from coingecko import CoinGeckoAPIError, CoinGeckoClient
from service import ScreenerService


class Coin(BaseModel):
    id: str
    symbol: str
    name: str
    market_cap: float
    fdv: float
    volume_24h: float
    tvl: float
    max_supply: float
    total_supply: float
    preview_listing: bool


class FilteredResponse(BaseModel):
    count: int
    cached_age_seconds: int
    coins: list[Coin]


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = CoinGeckoClient()
    app.state.service = ScreenerService(client)
    yield
    await client.close()


app = FastAPI(title="CoinGecko Screener", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/coins/filtered", response_model=FilteredResponse)
async def filtered_coins(refresh: bool = Query(False, description="Bypass cache")):
    service: ScreenerService = app.state.service
    try:
        coins = await service.get_filtered(refresh=refresh)
    except (httpx.HTTPError, CoinGeckoAPIError) as exc:
        raise HTTPException(status_code=502, detail=f"CoinGecko error: {exc}")
    return FilteredResponse(
        count=len(coins),
        cached_age_seconds=int(time.time() - service.cached_at),
        coins=coins,
    )