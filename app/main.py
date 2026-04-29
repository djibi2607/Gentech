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

@asynccontextmanager
async def lifespan (app: FastAPI):
    redis_url = os.getenv("REDIS_URL")

    try:
        redis = aioredis.from_url (redis_url)

        FastAPICache.init(RedisBackend(redis), prefix = "gentech-app-cache")
        yield

    finally:
        await redis.aclose()

app = FastAPI(lifespan = lifespan)

app.include_router(UserRoutes.router)
app.include_router(AdminRoutes.router)
app.include_router(AgentRoutes.router)
