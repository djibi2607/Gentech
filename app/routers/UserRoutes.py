from fastapi import APIRouter, Depends
from app.schemas.UserSchema import CreateUser, Login, refreshTok
from app.database import get_db
from app.services import UserServices
from sqlalchemy.orm import Session
from app.utils.Auth import get_current_user
from app.models.UserModel import User
from app.schemas.TransactionSchema import DepWith, Transfer

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

@router.post("/deposit")
async def deposit (data: DepWith, db: Session = Depends (get_db), current_user: User = Depends(get_current_user)):
    return await UserServices.deposit(data, db, current_user)

@router.post ("/withdraw")
async def deposit (data: DepWith, db: Session = Depends (get_db), current_user:User = Depends (get_current_user)):
    return await UserServices.withdraw(db,data,current_user)

@router.post("/transfer")
async def transfer (data: Transfer, db: Session = Depends (get_db), current_user: User = Depends (get_current_user)):
    return await UserServices.transfer(db, data, current_user)


