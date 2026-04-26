from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from app.routers import UserRoutes, AdminRoutes, AgentRoutes
from app.models.UserModel import User
from app.models.WalletModel import Wallet
from app.models.TransactionModel import Transaction
from app.models.RefreshModel import RefreshToken
from app.database import base, engine

app = FastAPI()

app.include_router(UserRoutes.router)
app.include_router(AdminRoutes.router)
app.include_router(AgentRoutes.router)

base.metadata.create_all( bind = engine)