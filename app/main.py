from fastapi import FastAPI
from app.routers import UserRoutes, AdminRoutes, AgentRoutes

app = FastAPI()

app.include_router(UserRoutes.router)
app.include_router(AdminRoutes.router)
app.include_router(AgentRoutes.router)


