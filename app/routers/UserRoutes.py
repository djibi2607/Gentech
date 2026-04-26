from fastapi import APIRouter, Depends
from app.schemas.UserSchema import CreateUser, Login, refreshTok
from app.database import get_db
from app.services import UserServices
from sqlalchemy.orm import Session

router = APIRouter(prefix = "/api/users")

@router.post("/signup")
async def signup (data:CreateUser, db: Session = Depends (get_db)):
    return await UserServices.signup(db, data)

@router.post("/login")
async def login (data : Login, db:Session = Depends(get_db)):
    return await UserServices.login(db,data)

@router.post("/refresh_token")
async def refreshToken (data: refreshTok, db: Session = Depends (get_db)):
    return await UserServices.refreshToken (data, db)