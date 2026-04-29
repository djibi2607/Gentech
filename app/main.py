from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from app.routers import UserRoutes, AdminRoutes, AgentRoutes
from app.models.UserModel import User
from app.models.WalletModel import Wallet
from app.models.TransactionModel import Transaction
from app.models.RefreshModel import RefreshToken
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.services.RatelimitExceeded import _rate_limit_exceeded_custom

@asynccontextmanager
async def lifespan (app: FastAPI):
    redis_url = os.getenv("REDIS_URL")

    try:
        redis = aioredis.from_url (redis_url)

        FastAPICache.init(RedisBackend(redis), prefix = "gentech-app-cache")
        yield

    finally:
        await redis.aclose()

limiter = Limiter (key_func = get_remote_address)

app = FastAPI(lifespan = lifespan)

app.state.limiter = limiter

app.include_router(UserRoutes.router)
app.include_router(AdminRoutes.router)
app.include_router(AgentRoutes.router)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_custom)